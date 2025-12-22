from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine

# Routers (à créer progressivement)
from app.api.router import api_router
from app.models.users import User
from app.models.tickets import Ticket

app = FastAPI(title="Ticketing Backend")

# ⬇️ CRÉATION DES TABLES AU DÉMARRAGE
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)



def create_app() -> FastAPI:
    """
    Factory de l'application FastAPI
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS (large pour hackathon)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(api_router)

    return app


# Create app
app = create_app()


# Optionnel : création automatique des tables
# ⚠️ À utiliser uniquement AVANT Alembic
# Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Health"])
def health_check():
    """
    Endpoint simple pour tester que l'API fonctionne
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENV,
    }
