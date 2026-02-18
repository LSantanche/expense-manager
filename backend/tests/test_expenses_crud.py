def test_expenses_crud_happy_path(client):
    payload = {
        "amount": "12.34",
        "currency": "EUR",
        "expense_date": "2026-02-01",
        "merchant": "Coffee Bar",
        "category": "food",
        "source": "manual",
        "needs_review": False,
    }

    # CREATE
    resp = client.post("/expenses", json=payload)
    assert resp.status_code == 201
    created = resp.json()
    expense_id = created["id"]
    assert created["merchant"] == "Coffee Bar"
    assert created["amount"] == "12.34"

    # LIST
    resp = client.get("/expenses")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == expense_id

    # GET
    resp = client.get(f"/expenses/{expense_id}")
    assert resp.status_code == 200
    got = resp.json()
    assert got["id"] == expense_id

    # PATCH (partial update)
    resp = client.patch(
        f"/expenses/{expense_id}",
        json={"merchant": "Coffee Bar 2", "needs_review": True},
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["merchant"] == "Coffee Bar 2"
    assert updated["needs_review"] is True

    # DELETE
    resp = client.delete(f"/expenses/{expense_id}")
    assert resp.status_code == 204

    # GET after delete -> 404
    resp = client.get(f"/expenses/{expense_id}")
    assert resp.status_code == 404


def test_expenses_not_found(client):
    assert client.get("/expenses/999999").status_code == 404
    assert client.patch("/expenses/999999", json={"merchant": "x"}).status_code == 404
    assert client.delete("/expenses/999999").status_code == 404
