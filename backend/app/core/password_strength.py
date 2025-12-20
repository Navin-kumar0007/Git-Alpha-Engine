"""
Password Strength Checker
Analyzes password strength and provides feedback
"""

import re
from typing import Tuple, List


def check_password_strength(password: str) -> dict:
    """
    Analyze password strength and provide feedback
    
    Args:
        password: Password to analyze
        
    Returns: dict with score, strength_text, feedback, and individual checks
    """
    score = 0
    feedback = []
    
    # Individual checks
    has_length = len(password) >= 8
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_numbers = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    # Calculate score
    if has_length:
        score += 1
    else:
        feedback.append("Use at least 8 characters")
    
    if has_uppercase:
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if has_lowercase:
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if has_numbers:
        score += 1
    else:
        feedback.append("Add numbers")
    
    if has_special:
        score += 1
    else:
        feedback.append("Add special characters (!@#$%^&*)")
    
    # Additional checks for very strong passwords
    if len(password) >= 12:
        score = min(score + 0.5, 5)
    
    if len(password) >= 16:
        score = min(score + 0.5, 5)
    
    # Normalize score to 0-4
    score = min(int(score), 4)
    
    # Determine strength text
    strength_levels = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Strong",
        4: "Very Strong"
    }
    strength_text = strength_levels.get(score, "Unknown")
    
    # If score is high, provide positive feedback
    if score >= 4:
        feedback = ["Excellent password strength!"]
    elif score == 3:
        feedback = ["Good password strength"] + feedback[:1]
    
    return {
        "score": score,
        "strength_text": strength_text,
        "feedback": feedback,
        "has_length": has_length,
        "has_uppercase": has_uppercase,
        "has_lowercase": has_lowercase,
        "has_numbers": has_numbers,
        "has_special": has_special
    }
