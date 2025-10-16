from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.models.schemas import TokenData, UserInDB
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)


def get_password_hash(password: str) -> str:
    # Truncate password to 72 characters
    return pwd_context.hash(password[:72])


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    if username == settings.default_username:
        # Allow plaintext default password in settings; hash if not already hashed
        stored_password = settings.default_password
        if not isinstance(stored_password, str):
            return None
        stored_hash = stored_password if stored_password.startswith("$2") else get_password_hash(stored_password)

        user = UserInDB(
            username=settings.default_username,
            hashed_password=stored_hash
        )
        if verify_password(password[:72], user.hashed_password):
            return user
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None