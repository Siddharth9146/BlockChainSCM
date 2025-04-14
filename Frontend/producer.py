import streamlit as st
from datetime import date
from utils import add_product, add_distributor, view_products

def producer_ui():
    st.header("👨‍🌾 Producer Dashboard")

    action = st.selectbox("Choose an action", ["Add Product", "Add Distributor", "My Products List", "View Products"])

    if action == "Add Product":
        st.subheader("📦 Add Product")

        product_name = st.text_input("Product Name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        location = st.text_input("Location")
        today = date.today()
        st.markdown(f"**Date:** {today}")

        # Upload Image and Description
        image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        description = st.text_area("Product Description")

        if st.button("Add Product"):
            if not all([product_name, category, quantity, location]):
                st.warning("Please fill all required fields.")
            else:
                result = add_product(product_name, category, quantity, location, str(today), image, description)
                if result["success"]:
                    st.success("Product added successfully!")
                else:
                    st.error("Failed to add product.")

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

        products = view_products()  # Replace with actual backend call
        if products:
            for p in products:
                st.write(f"**{p['name']}**")
                st.write(f"ID: {p['id']} | Date Created: {p['date_created']} | Status: {p['status']}")
        else:
            st.info("No products found.")
