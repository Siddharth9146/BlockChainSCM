import requests
import streamlit as st
from datetime import date
from utils import add_product, add_distributor, view_products

API_URL = "http://127.0.0.1:8000"  # Make sure the API URL is correct

def producer_ui():
    st.header("👨‍🌾 Producer Dashboard")

   
    action = st.selectbox("Choose an action", ["Add Product", "Add Distributor", "My Products List", "View Products"])

    if action == "Add Product":
        st.subheader("📦 Add Product")

        name = st.text_input("Product Name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        location = st.text_input("Location")
        today = date.today()
        st.markdown(f"**Date:** {today}")

        # Upload Image and Description
        image_url = st.text_input("Image URL")
        description = st.text_area("Product Description")

        if st.button("Add Product"):
            if not all([name, category, quantity, location]):
                st.warning("Please fill all required fields.")
            else:
                payload = {
                    'name': name,
                    'description': description,
                    'category': category,
                    'quantity': quantity,
                    'location': location,
                    'date': str(today),
                    'image_url': image_url,
                }
                headers = {
                    "Authorization": f"Bearer {token}"
                }
                response = requests.post(f"{API_URL}/product", json=payload, headers=headers)

                if response.status_code == 201:
                    st.success("Product added successfully!")
                else:
                    st.error(f"Failed to add product: {response.json().get('detail', 'Unknown error')}")

    elif action == "Add Distributor":
        st.subheader("🚛 Add Distributor")

        distributor_id = st.text_input("Distributor ID")
        distributor_name = st.text_input("Distributor Name")

        if st.button("Add Distributor"):
            if not distributor_id or not distributor_name:
                st.warning("Please provide both Distributor ID and Name.")
            else:
                result = add_distributor(distributor_id, distributor_name)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error("Failed to add distributor.")

    elif action == "View Products":
        st.subheader("📋 View Products")

        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(f"{API_URL}/products", headers=headers)
        if response.status_code == 200:
            products = response.json().get("products", [])
            if products:
                for p in products:
                    st.write(f"**{p['name']}**")
                    st.write(f"ID: {p['productId']} | Date Created: {p['date_created']} | Status: {p['status']}")
            else:
                st.info("No products found.")
        else:
            st.error("Failed to fetch products.")
