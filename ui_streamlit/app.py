import os
from datetime import date
from decimal import Decimal, InvalidOperation

import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def api_health() -> bool:
    try:
        with httpx.Client(timeout=3.0) as client:
            r = client.get(f"{API_BASE_URL}/health")
            return r.status_code == 200
    except httpx.RequestError:
        return False


def api_post_expense(payload: dict) -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.post(f"{API_BASE_URL}/expenses", json=payload)
        r.raise_for_status()
        return r.json()


def api_list_expenses(limit: int = 50, offset: int = 0) -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(
            f"{API_BASE_URL}/expenses",
            params={"limit": limit, "offset": offset},
        )
        r.raise_for_status()
        return r.json()


st.set_page_config(page_title="Expense Manager AI", layout="wide")
st.title("Expense Manager AI – Streamlit v1")
st.caption(f"Backend API: {API_BASE_URL}")

ok = api_health()
st.sidebar.success("Backend /health: OK") if ok else st.sidebar.error("Backend /health: KO (non raggiungibile)")

with st.sidebar:
    st.header("Inserisci spesa (manuale)")

    amount_str = st.text_input("Importo (es. 12.34)", value="0.00")
    currency = st.text_input("Valuta (ISO 4217)", value="EUR", max_chars=3)
    expense_date = st.date_input("Data", value=date.today())
    merchant = st.text_input("Merchant (opzionale)", value="")
    category = st.text_input("Categoria (opzionale)", value="")
    notes = st.text_area("Note (opzionale)", value="")

    submitted = st.button("Salva")

if submitted:
    # Validazione semplice lato UI per evitare float/rounding e input sporchi
    try:
        amount = Decimal(amount_str)
        if amount < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        st.error("Importo non valido. Usa un numero >= 0, ad esempio 12.34")
    else:
        payload = {
            "amount": str(amount),
            "currency": currency.strip().upper(),
            "expense_date": expense_date.isoformat(),
            "merchant": merchant.strip() or None,
            "category": category.strip() or None,
            "notes": notes.strip() or None,
            "source": "manual",
            "needs_review": False,
        }

        try:
            created = api_post_expense(payload)
            st.success(f"Spesa creata (id={created['id']})")
            st.rerun()
        except httpx.HTTPStatusError as e:
            st.error(f"Errore API ({e.response.status_code}): {e.response.text}")
        except httpx.RequestError as e:
            st.error(f"Backend non raggiungibile: {e}")

st.subheader("Spese recenti")

col1, col2 = st.columns([1, 3])
with col1:
    refresh = st.button("Aggiorna lista")

if refresh:
    st.rerun()

try:
    data = api_list_expenses(limit=50, offset=0)
    st.write(f"Totale: {data['total']}")
    st.dataframe(data["items"], use_container_width=True)
except httpx.RequestError as e:
    st.warning(f"Backend non raggiungibile: {e}")
except httpx.HTTPStatusError as e:
    st.error(f"Errore API ({e.response.status_code}): {e.response.text}")
