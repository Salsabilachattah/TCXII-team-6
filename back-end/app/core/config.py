from pydantic_settings import BaseSettings
from typing import Optional

class Config:
    env_file = ".env"
    
class Settings(BaseSettings):
    # =========================
    # APP
    # =========================
    APP_NAME: str
    ENV: str

    # =========================
    # DATABASE
    # =========================
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # =========================
    # SECURITY
    # =========================
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # =========================
    # EMAIL / SMTP (optional)
    # =========================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # Optional app URL for building reset links
    APP_URL: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "forbid"


settings = Settings()
