from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# Routes admin à implémenter plus tard
# Exemples :
# - statistiques
# - gestion agents
# - supervision tickets
