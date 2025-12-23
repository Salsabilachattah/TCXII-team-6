from pydantic import BaseModel
from typing import Optional


class AccessTokenPayload(BaseModel):
    user_id: int
    role: str


class RefreshTokenPayload(BaseModel):
    user_id: int

class ResetTokenPayload(BaseModel):
    user_id: int
