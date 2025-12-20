"""
OAuth Configuration and Utilities
Support for Google and GitHub OAuth authentication
"""

import os
from authlib.integrations.starlette_client import OAuth

# OAuth configuration - initialize without config file
oauth = OAuth()

# Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID', ''),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET', ''),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'read:user user:email'}
)


async def get_google_user_info(token):
    """
    Get user information from Google OAuth token
    
    Returns: dict with user_id, email, name
    """
    google = oauth.create_client('google')
    resp = await google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
    resp.raise_for_status()
    profile = resp.json()
    
    return {
        'user_id': profile.get('id'),
        'email': profile.get('email'),
        'name': profile.get('name'),
        'avatar_url': profile.get('picture')
    }


async def get_github_user_info(token):
    """
    Get user information from GitHub OAuth token
    
    Returns: dict with user_id, email, name
    """
    github = oauth.create_client('github')
    
    # Get user profile
    resp = await github.get('user', token=token)
    resp.raise_for_status()
    profile = resp.json()
    
    # Get primary email
    email_resp = await github.get('user/emails', token=token)
    email_resp.raise_for_status()
    emails = email_resp.json()
    
    primary_email = next(
        (email['email'] for email in emails if email.get('primary')),
        emails[0]['email'] if emails else None
    )
    
    return {
        'user_id': str(profile.get('id')),
        'email': primary_email,
        'name': profile.get('name') or profile.get('login'),
        'avatar_url': profile.get('avatar_url')
    }
