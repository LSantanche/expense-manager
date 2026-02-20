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


def api_list_expenses(params: dict) -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE_URL}/expenses", params=params)
        r.raise_for_status()
        return r.json()


st.set_page_config(page_title="Expense Manager AI", layout="wide")
st.title("Expense Manager AI – Streamlit v1")
st.caption(f"Backend API: {API_BASE_URL}")

# Stato UI: filtri + paginazione
if "filters" not in st.session_state:
    st.session_state["filters"] = {
        "merchant": "",
        "category": "",
        "source": "",
        "needs_review": "any",  # any|true|false
        "date_from": None,
        "date_to": None,
        "min_amount": "",
        "max_amount": "",
    }

if "pagination" not in st.session_state:
    st.session_state["pagination"] = {"limit": 50, "offset": 0}

ok = api_health()
if ok:
    st.sidebar.success("Backend /health: OK")
else:
    st.sidebar.error("Backend /health: KO (non raggiungibile)")

save_msg = st.sidebar.empty()
with st.sidebar:
    st.header("Inserisci spesa (manuale)")

    amount_str = st.text_input("Importo (es. 12.34)", value="0.00")
    amount_msg = st.empty()
    currency = st.text_input("Valuta (ISO 4217)", value="EUR", max_chars=3)
    expense_date = st.date_input("Data", value=date.today())
    merchant = st.text_input("Merchant (opzionale)", value="")
    category = st.text_input("Categoria (opzionale)", value="")
    notes = st.text_area("Note (opzionale)", value="")

    submitted = st.button("Salva")

    st.divider()
    st.header("Filtri lista")

    f = st.session_state["filters"]
    p = st.session_state["pagination"]

    f["merchant"] = st.text_input("Merchant contiene", value=f["merchant"])
    f["category"] = st.text_input("Categoria (esatta)", value=f["category"])
    f["source"] = st.selectbox("Source", options=["", "manual", "ocr"], index=0 if f["source"] == "" else (1 if f["source"] == "manual" else 2))

    f["needs_review"] = st.selectbox(
        "Needs review",
        options=["any", "true", "false"],
        index=["any", "true", "false"].index(f["needs_review"]),
    )

    c1, c2 = st.columns(2)
    with c1:
        f["date_from"] = st.date_input("Da (data)", value=f["date_from"])
    with c2:
        f["date_to"] = st.date_input("A (data)", value=f["date_to"])

    f["min_amount"] = st.text_input("Importo min (>=)", value=f["min_amount"])
    f["max_amount"] = st.text_input("Importo max (<=)", value=f["max_amount"])

    p["limit"] = st.selectbox("Righe per pagina", options=[20, 50, 100, 200], index=[20, 50, 100, 200].index(p["limit"]))

    apply_filters = st.button("Applica filtri")
    reset_filters = st.button("Reset filtri")

    if apply_filters:
        # Quando applichi nuovi filtri, riparti da pagina 1
        st.session_state["pagination"]["offset"] = 0
        st.rerun()

    if reset_filters:
        st.session_state["filters"] = {
            "merchant": "",
            "category": "",
            "source": "",
            "needs_review": "any",
            "date_from": None,
            "date_to": None,
            "min_amount": "",
            "max_amount": "",
        }
        st.session_state["pagination"] = {"limit": 50, "offset": 0}
        st.rerun()

if submitted:
    # Validazione semplice lato UI per evitare float/rounding e input sporchi
    amount_msg.empty()
    try:
        amount = Decimal(amount_str)
        if amount < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        amount_msg.error("Importo non valido. Usa un numero >= 0")
        st.stop() # Altrimenti il resto della pagina continua a renderizzare (chiamate api anche con input sbagliato)
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
    st.subheader("Spese")

    f = st.session_state["filters"]
    p = st.session_state["pagination"]

    # Costruzione params coerente con API
    params = {
        "limit": p["limit"],
        "offset": p["offset"],
    }

    if f["merchant"].strip():
        params["merchant"] = f["merchant"].strip()
    if f["category"].strip():
        params["category"] = f["category"].strip()
    if f["source"]:
        params["source"] = f["source"]

    if f["needs_review"] != "any":
        params["needs_review"] = True if f["needs_review"] == "true" else False

    if f["date_from"] is not None:
        params["date_from"] = f["date_from"].isoformat()
    if f["date_to"] is not None:
        params["date_to"] = f["date_to"].isoformat()

    # min/max amount: validazione leggera lato UI (se non parse, ignoriamo e avvisiamo)
    warnings = []
    try:
        if f["min_amount"].strip():
            params["min_amount"] = str(Decimal(f["min_amount"].strip()))
    except Exception:
        warnings.append("Importo min non valido: ignorato.")

    try:
        if f["max_amount"].strip():
            params["max_amount"] = str(Decimal(f["max_amount"].strip()))
    except Exception:
        warnings.append("Importo max non valido: ignorato.")

    for w in warnings:
        st.warning(w)

    try:
        data = api_list_expenses(params=params)
        items = data["items"]
        total = data["total"]

        st.write(f"Totale (filtrato): {total} — Offset: {p['offset']} — Limit: {p['limit']}")

        if total == 0:
            st.info("Nessun risultato con i filtri attuali.")
        else:
            st.dataframe(items, use_container_width=True)

        # Paginazione: Prev/Next
        prev_disabled = p["offset"] <= 0
        next_disabled = (p["offset"] + p["limit"]) >= total

        pc1, pc2, pc3 = st.columns([1, 1, 2])
        with pc1:
            if st.button("Prev", disabled=prev_disabled):
                st.session_state["pagination"]["offset"] = max(0, p["offset"] - p["limit"])
                st.rerun()
        with pc2:
            if st.button("Next", disabled=next_disabled):
                st.session_state["pagination"]["offset"] = p["offset"] + p["limit"]
                st.rerun()
        with pc3:
            st.caption("Tip: usa 'Needs review=true' per vedere rapidamente le spese da revisionare (HITL).")

    except httpx.RequestError as e:
        st.warning(f"Backend non raggiungibile: {e}")
    except httpx.HTTPStatusError as e:
        st.error(f"Errore API ({e.response.status_code}): {e.response.text}")
except httpx.RequestError as e:
    st.warning(f"Backend non raggiungibile: {e}")
except httpx.HTTPStatusError as e:
    st.error(f"Errore API ({e.response.status_code}): {e.response.text}")
