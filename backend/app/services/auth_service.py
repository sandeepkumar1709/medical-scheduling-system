from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Secret key from environment
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hardcoded users (username: hashed_password)
# Passwords: admin123, doctor123
USERS = {
    "admin": pwd_context.hash("admin123"),
    "doctor": pwd_context.hash("doctor123"),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate user against hardcoded users.
    Returns username if valid, None if invalid.
    """
    if username not in USERS:
        return None
    if not verify_password(password, USERS[username]):
        return None
    return username


def create_access_token(username: str) -> str:
    """Create a JWT token for the user."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": username,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return username.
    Returns None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
