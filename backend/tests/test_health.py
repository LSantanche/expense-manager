from fastapi.testclient import TestClient
from app.main import app

# TestClient simula un browser/client HTTP senza server
def test_health(): #N.B. pytest riconosce automaticamente le funzioni che iniziano con "test_"
    """
    Smoke Test: L'app si avvia e verifica che l'endpoint /health funzioni correttamente
    """
    # Crea un client di test collegato all'app (client che può fare richieste .get e .post)
    client = TestClient(app)

    # Simula una get all'endpoint /health
    resp = client.get("/health")

    # Faccio queste due verifiche, se false fallisce il test
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
