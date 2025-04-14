import streamlit as st

def regulator_ui():
    st.header("🕵️ Regulator Dashboard")

    product_id = st.text_input("Search Product by ID")

    if st.button("View Full Trace"):
        if product_id:
            st.write(f"Full Trace for Product ID {product_id}:")
            st.write("Origin: XYZ | All roles involved: Producer, Distributor, Retailer")
            st.write("Certification: Certified Organic")
            st.write("Compliance Status: Approved")
        else:
            st.warning("Please provide a Product ID.")
