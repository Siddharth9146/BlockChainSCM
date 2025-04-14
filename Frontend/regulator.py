import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def regulator_ui(token):
    st.header("🛂 Regulator Dashboard")
    headers = {"Authorization": f"Bearer {token}"}

    st.subheader("📋 All Products")
    response = requests.get(f"{API_URL}/products", headers=headers)
    if response.status_code == 200:
        for p in response.json()["products"]:
            st.write(f"🔸 **{p['name']}** - ID: {p['productId']}")
            st.write(f"Owner: {p['current_owner']} | Status: {p.get('status', 'N/A')}")
