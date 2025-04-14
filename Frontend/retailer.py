import streamlit as st
from utils import view_products

def retailer_ui():
    st.header("🏪 Retailer Dashboard")

    action = st.selectbox("Choose an action", ["Products Received", "Product Availability", "Product Trace View"])

    if action == "Products Received":
        st.subheader("📦 Products Received")

        products = view_products()  # Replace with actual call to get products received
        if products:
            for p in products:
                st.write(f"**{p['name']}** | ID: {p['id']} | Received On: {p['received_on']}")
        else:
            st.info("No products received.")

    elif action == "Product Availability":
        st.subheader("🛒 Product Availability")

        product_id = st.text_input("Product ID")
        price = st.number_input("Price", min_value=0.0, step=0.01)
        availability_status = st.selectbox("Availability Status", ["In Stock", "Out of Stock"])

        if st.button("Update Availability"):
            if not product_id:
                st.warning("Please provide Product ID.")
            else:
                st.success("Product availability updated successfully!")

    elif action == "Product Trace View":
        st.subheader("📜 Product Trace View")

        product_id = st.text_input("Product ID")

        if st.button("View Trace"):
            if product_id:
                st.write(f"Trace for Product ID {product_id}:")
                st.write("Origin: XYZ | Current Location: ABC | Roles involved: Producer, Distributor")
            else:
                st.warning("Please provide a Product ID.")
