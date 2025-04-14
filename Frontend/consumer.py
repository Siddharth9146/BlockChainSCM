import streamlit as st

def consumer_ui():
    st.header("🧍 Consumer Dashboard")

    product_id = st.text_input("Search by Product ID / QR Scan")

    if st.button("View Product Trace History"):
        if product_id:
            st.write(f"Trace for Product ID {product_id}:")
            st.write("Origin: XYZ | Locations: ABC, DEF | Roles involved: Producer, Distributor")
            st.write("Product Description: Fresh organic tomatoes. Certified by ABC Org.")
        else:
            st.warning("Please enter a Product ID.")
