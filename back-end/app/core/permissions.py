from typing import Iterable
from fastapi import Depends, HTTPException

from app.api.users.controller import get_current_user_from_token


def require_roles(*roles: Iterable[str]):
    """Dependency factory to require one or more roles (by name).

    Usage:
        current_user: User = Depends(require_roles("admin"))
        current_user: User = Depends(require_roles("agent", "admin"))
    """
    allowed = set(str(r) for r in roles)

    def _dependency(current_user=Depends(get_current_user_from_token)):
        if getattr(current_user, "role", None) in allowed:
            return current_user
        raise HTTPException(status_code=403, detail="Forbidden")

    return _dependency