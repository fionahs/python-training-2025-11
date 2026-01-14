from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import LoginRequest, Token, RefreshRequest, UserResponse
from app.utils.auth import verify_password
from app.utils.jwt import create_access_token, create_refresh_token, decode_token, hash_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # Rate limit for login to prevent brute force
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint - returns access token and refresh token

    Test with:
    - Email: admin@test.com
    - Password: AdminTest123!
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    # Create tokens
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.name
    }

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"user_id": user.id})

    # Store refresh token in database
    token_hash = hash_token(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db_refresh_token = RefreshToken(
        token_hash=token_hash,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_access_token(refresh_data: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Check if token exists in database and is not revoked
    token_hash = hash_token(refresh_data.refresh_token)
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False
    ).first()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or has been revoked"
        )

    # Check if token has expired
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )

    # Get user
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new access token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.name
    }
    access_token = create_access_token(data=token_data)

    # Return new access token with same refresh token
    return {
        "access_token": access_token,
        "refresh_token": refresh_data.refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    refresh_data: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout - revoke refresh token
    """
    # Revoke the refresh token
    token_hash = hash_token(refresh_data.refresh_token)
    db_token = db.query(RefreshToken).filter(
        token_hash == RefreshToken.token_hash,
        current_user.id == RefreshToken.user_id
    ).first()

    if db_token:
        db_token.revoked = True
        db.commit()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user information
    """
    return current_user
