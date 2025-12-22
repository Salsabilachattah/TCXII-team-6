from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

# Les routers seront ajoutés progressivement
# api_router.include_router(auth.router, tags=["Auth"])
# api_router.include_router(users.router, tags=["Users"])
# api_router.include_router(tickets.router, tags=["Tickets"])
# api_router.include_router(admin.router, tags=["Admin"])
