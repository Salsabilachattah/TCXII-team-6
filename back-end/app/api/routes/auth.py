from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from passlib.context import CryptContext
import jwt
import os
import httpx
import secrets
import hashlib
from fastapi.responses import RedirectResponse

from app.core.dependencies import get_db
from app.core.config import settings
from app.models.users import User
from app.api.routes.users import get_current_user_from_token
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from fastapi import BackgroundTasks
from app.utils.email import send_reset_email

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = "SECRET_KEY_HACKATHON"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# =========================
# UTILS
# =========================
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def hash_password(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# REGISTER (CLIENT ONLY)
# =========================
@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone_num=data.phone_num,
        date_naissance=data.date_naissance,
        gender=data.gender,
        profession=data.profession,
        hashed_password=hash_password(data.password),
        role="client",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_token(
        {"user_id": user.id, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        {"user_id": user.id},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    user.refresh_token = refresh_token
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# =========================
# LOGIN
# =========================
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token(
        {"user_id": user.id, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        {"user_id": user.id},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    user.refresh_token = refresh_token
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# =========================
# REFRESH TOKEN
# =========================
@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.refresh_token == data.refresh_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_token(
        {"user_id": user.id, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=data.refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# =========================
# LOGOUT
# =========================
@router.post("/logout")
def logout(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.refresh_token == data.refresh_token).first()
    if user:
        user.refresh_token = None
        db.commit()

    return {"message": "Logged out successfully"}


# =========================
# FORGOT PASSWORD (improved, no extra table)
# =========================
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Generate a one-time reset token, store its HASH and expiry on the user row.
    Response is intentionally generic to avoid account enumeration.
    In development, the plain token is returned to facilitate testing; in prod it should be emailed."""
    user = db.query(User).filter(User.email == data.email).first()

    # Generic response to avoid revealing whether the email exists
    generic = {"message": "If an account exists, a reset token has been generated and sent."}
    if not user:
        return generic

    # Generate opaque token and store its hash
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(hours=1)

    user.reset_token_hash = token_hash
    user.reset_token_expires_at = expires_at
    user.reset_token_used = False
    db.commit()

    # Build reset link (frontend should handle the token parameter)
    reset_link = f"{getattr(settings, 'APP_URL', '')}/reset-password?token={token}"

    # enqueue email sending (fire-and-forget)
    background_tasks.add_task(send_reset_email, user.email, reset_link)

    # For development/testing, return the token in response
    if getattr(settings, "ENV", "").lower() == "development":
        return {**generic, "reset_token": token}

    return generic


# =========================
# RESET PASSWORD (validate opaque token stored on user)
# =========================
@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(data.reset_token.encode()).hexdigest()

    user = (
        db.query(User)
        .filter(
            User.reset_token_hash == token_hash,
            User.reset_token_used == False,
            User.reset_token_expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = hash_password(data.new_password)
    user.reset_token_used = True
    user.reset_token_hash = None
    user.reset_token_expires_at = None
    # Invalidate sessions
    user.refresh_token = None
    db.commit()

    return {"message": "Password reset successful"}


# =========================
# CHANGE PASSWORD (authenticated)
# =========================
@router.post("/change-password")
def change_password(data: ChangePasswordRequest, current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    """Change password for authenticated user. Requires old_password and new_password."""

    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Old password is incorrect")

    current_user.hashed_password = hash_password(data.new_password)
    # Invalidate existing refresh token(s)
    current_user.refresh_token = None
    db.commit()

    return {"message": "Password changed successfully"}


# =========================
# GOOGLE OAUTH
# =========================
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


@router.get("/google/login")
def login_with_google():
    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )

    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(code: str, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to obtain access token from Google")
        token_response_data = token_response.json()
        access_token_google = token_response_data.get("access_token")
        id_token = token_response_data.get("id_token")

    if not access_token_google and not id_token:
        raise HTTPException(status_code=400, detail="Failed to obtain tokens from Google")

    # Fetch user info
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token_google}"} if access_token_google else {},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to obtain user info from Google")
        userinfo = userinfo_resp.json()

    email = userinfo.get("email")
    full_name = userinfo.get("name") or ""

    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    # Find or create local user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # split name into first/last
        parts = full_name.split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        # generate a random password hash so field is not empty
        random_pw = os.urandom(24).hex()
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_num=None,
            hashed_password=hash_password(random_pw),
            role="client",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # create tokens
    access_token = create_token(
        {"user_id": user.id, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        {"user_id": user.id},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    user.refresh_token = refresh_token
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
