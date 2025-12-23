from fastapi import HTTPException
from sqlalchemy.orm import Session
import secrets

from app.core.config import settings
from app.core.security import hash_password
from app.models.users import User
from app.schemas.user import AgentCreate, AgentResponse


def create_agent(data: AgentCreate, db: Session, temp_pw: str | None = None) -> dict | AgentResponse:
    """Business logic for creating an agent user. Returns either a dict with temp_password (dev) or AgentResponse."""

    # Check email not used
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with a generated temporary password (phone + first 3 letters)
    if temp_pw is None:
        if data.phone_num:
            temp_pw = f"{data.phone_num}{(data.first_name[:3].lower() if data.first_name else '')}"
        else:
            temp_pw = secrets.token_urlsafe(12)

    new_user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone_num=data.phone_num,
        date_naissance=data.date_naissance,
        gender=data.gender,
        profession=data.profession,
        hashed_password=hash_password(temp_pw),
        role="agent",
        is_active=True,
        must_change_password=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # In development, return the temporary password in response to allow quick testing
    if getattr(settings, "ENV", "").lower() == "development":
        resp = AgentResponse(id=new_user.id, email=new_user.email, first_name=new_user.first_name, last_name=new_user.last_name, role=new_user.role, is_active=new_user.is_active)
        return {**resp.dict(), "temp_password": temp_pw}

    return AgentResponse(id=new_user.id, email=new_user.email, first_name=new_user.first_name, last_name=new_user.last_name, role=new_user.role, is_active=new_user.is_active)
