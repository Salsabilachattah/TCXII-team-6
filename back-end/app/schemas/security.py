from pydantic import BaseModel
from typing import Optional


class AccessTokenPayload(BaseModel):
    user_id: int
    role: str
    # tu peux ajouter iat/exp en interne, mais pas nécessaire ici


class RefreshTokenPayload(BaseModel):
    user_id: int
    # exp/iat si tu veux, mais optionnel


class ResetTokenPayload(BaseModel):
    user_id: int
