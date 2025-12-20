"""
Two-Factor Authentication (2FA/MFA) Utilities
TOTP-based two-factor authentication using pyotp
"""

import pyotp
import qrcode
import io
import base64
from typing import Tuple
from cryptography.fernet import Fernet
import os

# Encryption key for secrets (should be in environment variable in production)
ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)

# Issuer name for authenticator apps
ISSUER_NAME = os.getenv("TWO_FACTOR_ISSUER", "Git-Alpha")


def generate_totp_secret() -> str:
    """
    Generate a new TOTP secret for a user
    Returns: base32 secret string
    """
    return pyotp.random_base32()


def generate_qr_code(secret: str, email: str) -> str:
    """
    Generate QR code for authenticator app setup
    
    Args:
        secret: TOTP secret
        email: User's email address
        
    Returns: Data URL containing QR code image
    """
    # Create provisioning URI for authenticator apps
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=email,
        issuer_name=ISSUER_NAME
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to data URL
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verify a TOTP code against a secret
    
    Args:
        secret: TOTP secret
        code: 6-digit code from user
        
    Returns: True if code is valid
    """
    totp = pyotp.TOTP(secret)
    # Allow 1 window before/after for clock skew
    return totp.verify(code, valid_window=1)


def encrypt_secret(secret: str) -> str:
    """
    Encrypt TOTP secret for storage in database
    
    Args:
        secret: Plain text secret
        
    Returns: Encrypted secret (base64 encoded)
    """
    encrypted = cipher.encrypt(secret.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_secret(encrypted_secret: str) -> str:
    """
    Decrypt TOTP secret from database
    
    Args:
        encrypted_secret: Encrypted secret (base64 encoded)
        
    Returns: Plain text secret
    """
    encrypted_bytes = base64.b64decode(encrypted_secret.encode())
    decrypted = cipher.decrypt(encrypted_bytes)
    return decrypted.decode()


def generate_backup_codes(count: int = 8) -> list:
    """
    Generate backup codes for 2FA recovery
    
    Args:
        count: Number of backup codes to generate
        
    Returns: List of backup codes
    """
    import secrets
    import string
    
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # Format as XXXX-XXXX for readability
        formatted = f"{code[:4]}-{code[4:]}"
        codes.append(formatted)
    
    return codes
