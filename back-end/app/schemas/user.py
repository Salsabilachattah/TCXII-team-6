from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_num: Optional[str] = None
    gender: Optional[str] = None
    date_naissance: Optional[date] = None
    profession: Optional[str] = None

    role: str
    is_active: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    # On autorise seulement la modification de certaines infos
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    gender: Optional[str] = Field(None, max_length=10)
    profession: Optional[str] = Field(None, max_length=100)
    date_naissance: Optional[date] = None
