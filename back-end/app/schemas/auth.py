from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


# =========================
# LOGIN
# =========================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# REGISTER (CLIENT / AGENT)
# =========================

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_num: Optional[str] = None
    date_naissance: Optional[date] = None
    password: str
    gender: Optional[str] = None
    profession: Optional[str] = None


# =========================
# TOKENS
# =========================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    must_change_password: bool | None = False


class RefreshTokenRequest(BaseModel):
    refresh_token: str




class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str



class RegisterResponse(BaseModel):
    message: str

