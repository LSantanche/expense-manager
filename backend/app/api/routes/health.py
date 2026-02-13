from fastapi import APIRouter

# APIRouter consente di aggiungere endpoint

# Creo un router. Il tags serve solamente per la documentazione
router = APIRouter(tags=["health"])

# Il decoratore @router indica che la funzione che viene subito sotto 
# risponde a una richiesta HTTP GET all’URL baseURL + "/health"
@router.get("/health")
def health():
    """
    Endpoint solo per verificare la salute del container
    """
    return {"status": "ok"}
