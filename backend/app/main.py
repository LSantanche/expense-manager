from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.expenses import router as expenses_router
from app.api.routes.health import router as health_router


def create_app() -> FastAPI:
    """Crea e configura l'app FastAPI"""
    app = FastAPI(title="Expense Manager AI", version="0.1.0")

    # Includo il router health
    app.include_router(health_router)
    
    # Router CRUD spese
    app.include_router(expenses_router)
    
    # Router per caricamento documenti
    app.include_router(documents_router)
    
    return app


app = create_app()
