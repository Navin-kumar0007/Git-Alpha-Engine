from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from starlette.responses import RedirectResponse
import uuid

from .. import models, schemas
from ..db import get_db
from ..core.security import (
    verify_password, get_password_hash, create_access_token, 
    get_current_user, create_session, revoke_session, revoke_all_sessions
)
from ..core import two_factor
from ..core.password_strength import check_password_strength
from ..core.oauth import oauth, get_google_user_info, get_github_user_info

router = APIRouter(prefix="/api")


# ========================================
# Basic Authentication
# ========================================

@router.post("/register")
def register(user_in: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user"""
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create session
    access_token, jti, expires_at = create_access_token({"sub": str(user.id)}, remember_me=False)
    device_info = request.headers.get("user-agent", "Unknown")
    ip_address = request.client.host if request.client else None
    create_session(db, user.id, jti, expires_at, device_info, ip_address)
    
    return {"status": "success", "user": schemas.UserOut.from_orm(user), "access_token": access_token}


@router.post("/login")
def login(user_in: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login with email/password and optional 2FA"""
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Check if 2FA is enabled
    if user.two_factor_enabled:
        if not user_in.totp_code:
            # User needs to provide 2FA code
            return {
                "requires_2fa": True,
                "message": "2FA code required"
            }
        
        # Verify 2FA code
        decrypted_secret = two_factor.decrypt_secret(user.two_factor_secret)
        if not two_factor.verify_totp_code(decrypted_secret, user_in.totp_code):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid 2FA code")
    
    # Auto-rehash password if using old pbkdf2 format (migrate to bcrypt)
    if user.hashed_password and user.hashed_password.startswith("$pbkdf2"):
        user.hashed_password = get_password_hash(user_in.password)
        db.commit()

    
    # Create token and session
    access_token, jti, expires_at = create_access_token(
        {"sub": str(user.id)},
        remember_me=user_in.remember_me
    )
    
    device_info = request.headers.get("user-agent", "Unknown")
    ip_address = request.client.host if request.client else None
    create_session(db, user.id, jti, expires_at, device_info, ip_address)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserOut.from_orm(user)
    }


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# ========================================
# 2FA / MFA Endpoints
# ========================================

@router.post("/auth/2fa/setup", response_model=schemas.TwoFactorSetup)
def setup_2fa(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate 2FA secret and QR code for setup"""
    if current_user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA already enabled")
    
    # Generate new secret
    secret = two_factor.generate_totp_secret()
    qr_code_url = two_factor.generate_qr_code(secret, current_user.email)
    backup_codes = two_factor.generate_backup_codes()
    
    # Store encrypted secret temporarily (not active yet)
    encrypted_secret = two_factor.encrypt_secret(secret)
    current_user.two_factor_secret = encrypted_secret
    db.commit()
    
    return {
        "secret": secret,
        "qr_code_url": qr_code_url,
        "backup_codes": backup_codes
    }


@router.post("/auth/2fa/verify-setup")
def verify_2fa_setup(
    verify_data: schemas.TwoFactorVerify,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify and enable 2FA"""
    if current_user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA already enabled")
    
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
    
    # Verify the code
    decrypted_secret = two_factor.decrypt_secret(current_user.two_factor_secret)
    if not two_factor.verify_totp_code(decrypted_secret, verify_data.code):
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Enable 2FA
    current_user.two_factor_enabled = True
    db.commit()
    
    return {"status": "success", "message": "2FA enabled successfully"}


@router.post("/auth/2fa/disable")
def disable_2fa(
    verify_data: schemas.TwoFactorVerify,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA after verification"""
    if not current_user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    # Verify the code before disabling
    decrypted_secret = two_factor.decrypt_secret(current_user.two_factor_secret)
    if not two_factor.verify_totp_code(decrypted_secret, verify_data.code):
        raise HTTPException(status_code=400, detail="Invalid verification code")  
    
    # Disable 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.commit()
    
    return {"status": "success", "message": "2FA disabled successfully"}


@router.get("/auth/2fa/status", response_model=schemas.TwoFactorStatusOut)
def get_2fa_status(current_user: models.User = Depends(get_current_user)):
    """Get 2FA status for current user"""
    return {
        "enabled": current_user.two_factor_enabled,
        "setup_required": False
    }


# ========================================
# Session Management
# ========================================

@router.get("/auth/sessions", response_model=schemas.SessionListOut)
def list_sessions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all active sessions for current user"""
    sessions = db.query(models.Session).filter(
        models.Session.user_id == current_user.id,
        models.Session.is_active == True
    ).order_by(models.Session.last_active.desc()).all()
    
    # Get current session JTI from token (would need to pass this from get_current_user)
    # For now, mark the most recent as current
    current_session_id = sessions[0].id if sessions else None
    
    session_list = []
    for sess in sessions:
        sess_out = schemas.SessionOut.from_orm(sess)
        sess_out.is_current = (sess.id == current_session_id)
        session_list.append(sess_out)
    
    return {
        "current_session_id": current_session_id or 0,
        "sessions": session_list
    }


@router.delete("/auth/sessions/{session_id}")
def revoke_specific_session(
    session_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    success = revoke_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "success", "message": "Session revoked"}


@router.delete("/auth/sessions/all")
def revoke_all_other_sessions(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke all sessions except current"""
    # TODO: Get current JTI from token
    count = revoke_all_sessions(db, current_user.id, except_jti=None)
    
    return {"status": "success", "message": f"Revoked {count} sessions"}


# ========================================
# Password Strength Checker
# ========================================

@router.post("/auth/password-strength", response_model=schemas.PasswordStrengthOut)
def check_password(password_data: schemas.PasswordStrengthCheck):
    """Check password strength"""
    result = check_password_strength(password_data.password)
    return result


# ========================================
# OAuth Endpoints
# ========================================

import os
from urllib.parse import urlencode
import secrets

@router.get("/auth/oauth/google")
async def google_login(request: Request):
    """Redirect to Google OAuth"""
    # Build authorization URL manually (stateless)
    params = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'redirect_uri': str(request.url_for('google_callback')),
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/auth/oauth/google/callback")
async def google_callback(request: Request, code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for token manually
        import httpx
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': str(request.url_for('google_callback')),
            'grant_type': 'authorization_code'
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token = token_response.json()
        
        # Get user info from Google
        async with httpx.AsyncClient() as client:
            user_info_response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f"Bearer {token['access_token']}"}
            )
            user_info_response.raise_for_status()
            google_user = user_info_response.json()
        
        user_info = {
            'user_id': google_user.get('id'),
            'email': google_user.get('email'),
            'name': google_user.get('name'),
            'avatar_url': google_user.get('picture')
        }
        
        if not user_info.get('email'):
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if OAuth account exists
        oauth_account = db.query(models.OAuthAccount).filter(
            models.OAuthAccount.provider == 'google',
            models.OAuthAccount.provider_user_id == user_info['user_id']
        ).first()
        
        if oauth_account:
            # User already linked, login
            user = oauth_account.user
        else:
            # Check if user exists with this email
            user = db.query(models.User).filter(
                models.User.email == user_info['email']
            ).first()
            
            if not user:
                # Create new user
                user = models.User(
                    email=user_info['email'],
                    name=user_info.get('name', user_info['email'].split('@')[0]),
                    avatar_url=user_info.get('avatar_url'),
                    hashed_password=get_password_hash(str(uuid.uuid4()))  # Random password
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Link OAuth account
            oauth_account = models.OAuthAccount(
                user_id=user.id,
                provider='google',
                provider_user_id=user_info['user_id'],
                email=user_info['email'],
                access_token=token.get('access_token'),
                refresh_token=token.get('refresh_token')
            )
            db.add(oauth_account)
            db.commit()
        
        # Create session
        access_token, jti, expires_at = create_access_token(
            {"sub": str(user.id)},
            remember_me=True  # OAuth logins get remember_me by default
        )
        
        device_info = request.headers.get("user-agent", "Unknown")
        ip_address = request.client.host if request.client else None
        create_session(db, user.id, jti, expires_at, device_info, ip_address)
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:5173/?token={access_token}&provider=google"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        print(f"OAuth error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")



@router.get("/auth/oauth/github")
async def github_login(request: Request):
    """Redirect to GitHub OAuth"""
    # Build authorization URL manually (stateless)
    params = {
        'client_id': os.getenv('GITHUB_CLIENT_ID'),
        'redirect_uri': str(request.url_for('github_callback')),
        'scope': 'read:user user:email'
    }
    
    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/auth/oauth/github/callback")
async def github_callback(request: Request, code: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    try:
        # Exchange code for token manually
        import httpx
        
        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            'code': code,
            'client_id': os.getenv('GITHUB_CLIENT_ID'),
            'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
            'redirect_uri': str(request.url_for('github_callback'))
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data=token_data,
                headers={'Accept': 'application/json'}
            )
            token_response.raise_for_status()
            token = token_response.json()
        
        # Get user info from GitHub
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f"Bearer {token['access_token']}"}
            )
            user_response.raise_for_status()
            github_user = user_response.json()
            
            # Get email
            email_response = await client.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f"Bearer {token['access_token']}"}
            )
            email_response.raise_for_status()
            emails = email_response.json()
        
        # Get primary email
        primary_email = next(
            (email['email'] for email in emails if email.get('primary')),
            emails[0]['email'] if emails else None
        )
        
        user_info = {
            'user_id': str(github_user.get('id')),
            'email': primary_email,
            'name': github_user.get('name') or github_user.get('login'),
            'avatar_url': github_user.get('avatar_url')
        }
        
        if not user_info.get('email'):
            raise HTTPException(status_code=400, detail="Email not provided by GitHub")
        
        # Check if OAuth account exists
        oauth_account = db.query(models.OAuthAccount).filter(
            models.OAuthAccount.provider == 'github',
            models.OAuthAccount.provider_user_id == user_info['user_id']
        ).first()
        
        if oauth_account:
            # User already linked, login
            user = oauth_account.user
        else:
            # Check if user exists with this email
            user = db.query(models.User).filter(
                models.User.email == user_info['email']
            ).first()
            
            if not user:
                # Create new user
                user = models.User(
                    email=user_info['email'],
                    name=user_info.get('name', user_info['email'].split('@')[0]),
                    avatar_url=user_info.get('avatar_url'),
                    hashed_password=get_password_hash(str(uuid.uuid4()))  # Random password
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Link OAuth account
            oauth_account = models.OAuthAccount(
                user_id=user.id,
                provider='github',
                provider_user_id=user_info['user_id'],
                email=user_info['email'],
                access_token=token.get('access_token'),
                refresh_token=token.get('refresh_token')
            )
            db.add(oauth_account)
            db.commit()
        
        # Create session
        access_token, jti, expires_at = create_access_token(
            {"sub": str(user.id)},
            remember_me=True  # OAuth logins get remember_me by default
        )
        
        device_info = request.headers.get("user-agent", "Unknown")
        ip_address = request.client.host if request.client else None
        create_session(db, user.id, jti, expires_at, device_info, ip_address)
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:5173/?token={access_token}&provider=github"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        print(f"GitHub OAuth error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")



@router.get("/auth/oauth/accounts", response_model=List[schemas.OAuthAccountOut])
def get_oauth_accounts(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get connected OAuth accounts for current user"""
    accounts = db.query(models.OAuthAccount).filter(
        models.OAuthAccount.user_id == current_user.id
    ).all()
    return accounts


@router.delete("/auth/oauth/accounts/{provider}")
def disconnect_oauth_account(
    provider: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect an OAuth account"""
    account = db.query(models.OAuthAccount).filter(
        models.OAuthAccount.user_id == current_user.id,
        models.OAuthAccount.provider == provider
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="OAuth account not found")
    
    db.delete(account)
    db.commit()
    
    return {"status": "success", "message": f"{provider.capitalize()} account disconnected"}
