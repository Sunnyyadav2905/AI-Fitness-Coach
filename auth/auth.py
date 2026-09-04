"""
auth/auth.py - Authentication Module for AI-FitCoach
Handles password hashing via bcrypt (with werkzeug/hashlib fallback),
user registration, credential validation, and authentication verification.
"""

from typing import Tuple, Optional, Dict, Any
from database import db
from utils.validators import validate_email, validate_password

try:
    import bcrypt

    def hash_password(password: str) -> str:
        """Hashes a raw password securely using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(password: str, hashed: str) -> bool:
        """Verifies a plain password against its hashed representation."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            # Fallback check if old hash format
            if hashed.startswith("pbkdf2:"):
                import hashlib
                parts = hashed.split(":")
                if len(parts) == 4:
                    salt = parts[2]
                    stored_h = parts[3]
                    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
                    return h == stored_h
            return False

except ImportError:
    try:
        from werkzeug.security import generate_password_hash, check_password_hash

        def hash_password(password: str) -> str:
            return generate_password_hash(password)

        def verify_password(password: str, hashed: str) -> bool:
            return check_password_hash(hashed, password)
    except ImportError:
        import hashlib
        import secrets

        def hash_password(password: str) -> str:
            salt = secrets.token_hex(16)
            h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
            return f"pbkdf2:sha256:{salt}:{h}"

        def check_password_hash(p_hash: str, password: str) -> bool:
            try:
                parts = p_hash.split(":")
                if len(parts) == 4:
                    salt = parts[2]
                    stored_h = parts[3]
                    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
                    return h == stored_h
                return False
            except Exception:
                return False

        def verify_password(password: str, hashed: str) -> bool:
            return check_password_hash(hashed, password)


def register_user(
    username: str,
    email: str,
    password: str,
    confirm_password: Optional[str] = None,
    name: str = "",
    db_path: Optional[str] = None
) -> Tuple[bool, str, Optional[int]]:
    """
    Registers a new user after strict input validation.
    Returns (success, message, user_id).
    """
    username = (username or "").strip()
    email = (email or "").strip().lower()

    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long.", None

    valid_email, email_err = validate_email(email)
    if not valid_email:
        return False, email_err, None

    valid_pwd, pwd_err = validate_password(password)
    if not valid_pwd:
        return False, pwd_err, None

    if confirm_password is not None and password != confirm_password:
        return False, "Passwords do not match.", None

    if db.get_user_by_username(username, db_path=db_path):
        return False, "Username is already taken.", None

    if db.get_user_by_email(email, db_path=db_path):
        return False, "An account with this email already exists.", None

    hashed = hash_password(password)
    user_id = db.create_user(username, email, hashed, db_path=db_path)

    if not user_id:
        return False, "Database error creating user account.", None

    # Initialize default user profile
    db.save_profile(
        user_id=user_id,
        name=name or username.capitalize(),
        age=25,
        gender="Male",
        height=170.0,
        weight=70.0,
        activity_level="Moderately Active",
        fitness_goal="Weight Loss",
        target_weight=65.0,
        db_path=db_path
    )

    return True, "Account registered successfully! You can now log in.", user_id


def signup_user(
    username: str, email: str, password: str, full_name: str = "", db_path: Optional[str] = None
) -> Tuple[bool, str, Optional[int]]:
    """Alias for register_user for backwards compatibility."""
    return register_user(
        username=username,
        email=email,
        password=password,
        confirm_password=password,
        name=full_name,
        db_path=db_path
    )


def authenticate_user(
    username_or_email: str, password: str, db_path: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates a user via username or email address.
    Returns (success, message, user_dict).
    """
    identifier = (username_or_email or "").strip().lower()
    if not identifier or not password:
        return False, "Please enter both username/email and password.", None

    user = db.get_user_by_username(identifier, db_path=db_path)
    if not user:
        user = db.get_user_by_email(identifier, db_path=db_path)

    if not user:
        return False, "Invalid username or password.", None

    if not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password.", None

    return True, "Login successful!", user


def login_user(
    username_or_email: str, password: str, db_path: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Alias for authenticate_user."""
    return authenticate_user(username_or_email, password, db_path=db_path)

