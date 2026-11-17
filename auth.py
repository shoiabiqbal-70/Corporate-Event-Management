
"""
Authentication and JWT security for Corporate Event Management API.

Handles password hashing, employee registration, login,
JWT creation, and current-user verification.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from pwdlib import PasswordHash

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from env import settings
from models import User
from schemas import UserCreate, UserLogin, Token


# =========================================================
# 1. PASSWORD SECURITY
# =========================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plain password into a secure password hash."""

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored hash."""

    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# =========================================================
# 2. JWT TOKEN CREATION
# =========================================================

def create_access_token(user_id: int) -> str:
    """Generate a signed JWT access token."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    encoded_token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_token


# =========================================================
# 3. REGISTER EMPLOYEE
# =========================================================

async def register_user(
    db: AsyncSession,
    user_data: UserCreate,
):
    """Create a new employee account."""

    # Check whether email is already registered.
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create employee with hashed password.
    new_user = User(
        name=user_data.name,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    return new_user


# =========================================================
# 4. AUTHENTICATE EMPLOYEE
# =========================================================

async def authenticate_user(
    db: AsyncSession,
    login_data: UserLogin,
):
    """Verify employee login credentials."""

    result = await db.execute(
        select(User).where(
            User.email == str(login_data.email)
        )
    )

    user = result.scalar_one_or_none()

    if not user or not verify_password(
        login_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive.",
        )

    # Generate JWT after successful login.
    access_token = create_access_token(user.id)

    return Token(access_token=access_token)


# =========================================================
# 5. JWT SECURITY SCHEME
# =========================================================

bearer_scheme = HTTPBearer(
    auto_error=False,
)


# =========================================================
# 6. GET CURRENT AUTHENTICATED USER
# =========================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
):
    """Decode JWT and retrieve the authenticated employee."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token.",
            )

        user_id = int(user_id)

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    return user
