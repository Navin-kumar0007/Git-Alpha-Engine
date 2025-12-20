from datetime import datetime, timedelta
from typing import Optional
import os
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REMEMBER_ME_DAYS = int(os.getenv("SESSION_REMEMBER_ME_DAYS", "30"))

pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, remember_me: bool = False, expires_delta: Optional[timedelta] = None) -> tuple:
    """
    Create JWT access token with session tracking
    
    Args:
        data: Payload data (should include 'sub' for user_id)
        remember_me: If True, create longer-lived token
        expires_delta: Optional custom expiration
        
    Returns: Tuple of (token, jti, expires_at)
    """
    to_encode = data.copy()
    
    # Generate unique JWT ID for session tracking
    jti = str(uuid.uuid4())
    to_encode["jti"] = jti
    
    # Set expiration based on remember_me flag
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    elif remember_me:
        expire = datetime.utcnow() + timedelta(days=REMEMBER_ME_DAYS)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt, jti, expire


def create_session(
    db: Session,
    user_id: int,
    token_jti: str,
    expires_at: datetime,
    device_info: Optional[str] = None,
    ip_address: Optional[str] = None
) -> models.Session:
    """
    Create a new session record in database
    
    Args:
        db: Database session
        user_id: User ID
        token_jti: JWT ID from token
        expires_at: Token expiration time
        device_info: Browser/device information
        ip_address: Client IP address
        
    Returns: Created session object
    """
    # Deactivate old expired sessions
    db.query(models.Session).filter(
        models.Session.user_id == user_id,
        models.Session.expires_at < datetime.utcnow()
    ).update({"is_active": False})
    
    session = models.Session(
        user_id=user_id,
        token_jti=token_jti,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


def get_session_by_jti(db: Session, jti: str) -> Optional[models.Session]:
    """
    Get session by JWT ID
    """
    return db.query(models.Session).filter(
        models.Session.token_jti == jti,
        models.Session.is_active == True
    ).first()


def revoke_session(db: Session, session_id: int, user_id: int) -> bool:
    """
    Revoke a specific session
    
    Returns: True if successful
    """
    session = db.query(models.Session).filter(
        models.Session.id == session_id,
        models.Session.user_id == user_id
    ).first()
    
    if session:
        session.is_active = False
        db.commit()
        return True
    return False


def revoke_all_sessions(db: Session, user_id: int, except_jti: Optional[str] = None) -> int:
    """
    Revoke all sessions for a user except optionally one
    
    Returns: Number of sessions revoked
    """
    query = db.query(models.Session).filter(
        models.Session.user_id == user_id,
        models.Session.is_active == True
    )
    
    if except_jti:
        query = query.filter(models.Session.token_jti != except_jti)
    
    count = query.update({"is_active": False})
    db.commit()
    return count


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"DEBUG: Received token: {token[:20]}...")  # Print first 20 chars
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: Decoded payload: {payload}")
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")  # Get JWT ID
        print(f"DEBUG: User ID from token: {user_id}, JTI: {jti}")
        if user_id is None:
            print("DEBUG: No user_id in payload")
            raise credentials_exception
        
        # Validate session if JTI is present
        if jti:
            session = get_session_by_jti(db, jti)
            if not session or not session.is_active:
                print("DEBUG: Session is invalid or revoked")
                raise credentials_exception
            # Update last_active timestamp
            session.last_active = datetime.utcnow()
            db.commit()
        
    except JWTError as e:
        print(f"DEBUG: JWT Error: {e}")
        raise credentials_exception
    user =db.query(models.User).filter(models.User.id == int(user_id)).first()
    print(f"DEBUG: Found user: {user}")
    if user is None:
        print("DEBUG: User not found in database")
        raise credentials_exception
    return user
