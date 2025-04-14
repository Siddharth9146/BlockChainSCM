import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def distributor_ui(token):
    st.header("🚚 Distributor Dashboard")
    headers = {"Authorization": f"Bearer {token}"}

    st.subheader("📦 My Products")
    response = requests.get(f"{API_URL}/products", headers=headers)
    if response.status_code == 200:
        products = response.json()["products"]
        for product in products:
            st.write(f"**{product['name']}** - {product['productId']}")
            with st.expander("Update Status"):
                new_status = st.text_input("New Status", key=product['productId'])
                note = st.text_input("Note", key=product['productId'] + "_note")
                if st.button("Update", key=product['productId'] + "_update"):
                    payload = {
                        "status": new_status,
                        "note": note
                    }
                    res = requests.put(f"{API_URL}/product/{product['productId']}", json=payload, headers=headers)
                    if res.status_code == 200:
                        st.success("Updated successfully")
                    else:
                        st.error("Update failed")
