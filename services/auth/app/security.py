import re
import html
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator
import bcrypt
import secrets
import string

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation and sanitization utilities."""
    
    # Common attack patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"].*['\"]\s*=\s*['\"].*['\"])",
        r"(\b(OR|AND)\s+.*\s*LIKE\s*.*)",
        r"(\b(OR|AND)\s+.*\s*IN\s*\(.*\))",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<link[^>]*>.*?</link>",
        r"<meta[^>]*>.*?</meta>",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
        r"\.\.%2f",
        r"\.\.%5c",
    ]
    
    @classmethod
    def sanitize_input(cls, input_data: Any) -> Any:
        """Sanitize input data to prevent injection attacks."""
        if isinstance(input_data, str):
            # HTML escape
            sanitized = html.escape(input_data)
            
            # Remove null bytes
            sanitized = sanitized.replace('\x00', '')
            
            # Trim whitespace
            sanitized = sanitized.strip()
            
            return sanitized
        
        elif isinstance(input_data, dict):
            return {key: cls.sanitize_input(value) for key, value in input_data.items()}
        
        elif isinstance(input_data, list):
            return [cls.sanitize_input(item) for item in input_data]
        
        return input_data
    
    @classmethod
    def validate_sql_injection(cls, input_data: str) -> bool:
        """Check for SQL injection patterns."""
        if not isinstance(input_data, str):
            return True
        
        input_upper = input_data.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_upper, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def validate_xss(cls, input_data: str) -> bool:
        """Check for XSS patterns."""
        if not isinstance(input_data, str):
            return True
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_data, re.IGNORECASE):
                logger.warning(f"XSS pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def validate_path_traversal(cls, input_data: str) -> bool:
        """Check for path traversal patterns."""
        if not isinstance(input_data, str):
            return True
        
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, input_data, re.IGNORECASE):
                logger.warning(f"Path traversal pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def validate_input(cls, input_data: str, input_type: str = "general") -> bool:
        """Comprehensive input validation."""
        if not isinstance(input_data, str):
            return True
        
        # Basic length check
        if len(input_data) > 1000:
            logger.warning(f"Input too long: {len(input_data)} characters")
            return False
        
        # Check for SQL injection
        if not cls.validate_sql_injection(input_data):
            return False
        
        # Check for XSS
        if not cls.validate_xss(input_data):
            return False
        
        # Check for path traversal
        if not cls.validate_path_traversal(input_data):
            return False
        
        return True

class PasswordValidator:
    """Password validation and security utilities."""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        result = {
            "valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(password) < 8:
            result["valid"] = False
            result["issues"].append("Password must be at least 8 characters long")
        else:
            result["score"] += 1
        
        if not re.search(r"[a-z]", password):
            result["issues"].append("Password must contain at least one lowercase letter")
        else:
            result["score"] += 1
        
        if not re.search(r"[A-Z]", password):
            result["issues"].append("Password must contain at least one uppercase letter")
        else:
            result["score"] += 1
        
        if not re.search(r"\d", password):
            result["issues"].append("Password must contain at least one number")
        else:
            result["score"] += 1
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            result["issues"].append("Password must contain at least one special character")
        else:
            result["score"] += 1
        
        # Check for common passwords
        common_passwords = [
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey"
        ]
        
        if password.lower() in common_passwords:
            result["valid"] = False
            result["issues"].append("Password is too common")
        
        # Check for repeated characters
        if re.search(r"(.)\1{2,}", password):
            result["issues"].append("Password contains too many repeated characters")
        
        return result
    
    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """Generate a secure random password."""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

class TokenValidator:
    """JWT token validation and security utilities."""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """Validate token format."""
        if not token or len(token) < 10:
            return False
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', token):
            return False
        
        return True

# Enhanced Pydantic models with security validation
class SecureUserCreate(BaseModel):
    username: str
    email: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not SecurityValidator.validate_input(v, "username"):
            raise ValueError("Invalid username format")
        
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        
        return SecurityValidator.sanitize_input(v)
    
    @validator('email')
    def validate_email(cls, v):
        if not SecurityValidator.validate_input(v, "email"):
            raise ValueError("Invalid email format")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        
        return SecurityValidator.sanitize_input(v).lower()
    
    @validator('password')
    def validate_password(cls, v):
        if not SecurityValidator.validate_input(v, "password"):
            raise ValueError("Invalid password format")
        
        validation_result = PasswordValidator.validate_password_strength(v)
        if not validation_result["valid"]:
            raise ValueError(f"Password validation failed: {', '.join(validation_result['issues'])}")
        
        return v

class SecureUserLogin(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not SecurityValidator.validate_input(v, "username"):
            raise ValueError("Invalid username format")
        
        return SecurityValidator.sanitize_input(v)
    
    @validator('password')
    def validate_password(cls, v):
        if not SecurityValidator.validate_input(v, "password"):
            raise ValueError("Invalid password format")
        
        return v
