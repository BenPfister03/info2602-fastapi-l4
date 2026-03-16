# app/auth.py
from pwdlib import PasswordHash
from app.models import *
from app.database import SessionDep
from sqlmodel import select
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError

# JWT settings
SECRET_KEY = "ThisIsAnExampleOfWhatNotToUseAsTheSecretKeyIRL"
ALGORITHM = "HS256"

# Password hashing
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Encrypt password
def encrypt_password(password: str):
    return password_hash.hash(password)

# Verify password
def verify_password(plaintext_password: str, encrypted_password):
    return password_hash.verify(password=plaintext_password, hash=encrypted_password)

# Create JWT token using username as "sub"
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from JWT
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub", None)
        user_role = payload.get("role", None)
        if not username or not user_role:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    # Query the correct table based on role
    if user_role == "admin":
        user = db.exec(select(Admin).where(Admin.username == username)).one_or_none()
    else:  # regular_user
        user = db.exec(select(RegularUser).where(RegularUser.username == username)).one_or_none()

    if not user:
        raise credentials_exception

    return user

# **This is required for the routers**
AuthDep = Annotated[User, Depends(get_current_user)]
