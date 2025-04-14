import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def retailer_ui(token):
    st.header("🏬 Retailer Dashboard")
    headers = {"Authorization": f"Bearer {token}"}

    st.subheader("📦 My Inventory")
    response = requests.get(f"{API_URL}/products", headers=headers)
    if response.status_code == 200:
        products = response.json()["products"]
        for product in products:
            st.write(f"{product['name']} ({product['productId']})")
            st.write(f"Status: {product.get('status', 'N/A')}")
    else:
        st.warning("No products found.")
