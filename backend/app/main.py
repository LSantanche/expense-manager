from fastapi import FastAPI
from app.api.routes.health import router as health_router

# Crea l'app FastAPI
def create_app() -> FastAPI:
    app = FastAPI(title="Expense Manager AI", version="0.1.0")

    # Includo il router health
    app.include_router(health_router)
    return app


app = create_app()
