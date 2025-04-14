import streamlit as st
from utils import view_products, add_distributor

def distributor_ui():
    st.header("🚚 Distributor Dashboard")

    action = st.selectbox("Choose an action", ["Assigned Products", "Update Product Location", "Product Trace View"])

    if action == "Assigned Products":
        st.subheader("📋 Assigned/Available Products List")

        products = view_products()  # Replace with actual call to get assigned products
        if products:
            for p in products:
                st.write(f"**{p['name']}** | ID: {p['id']} | Location: {p['location']}")
        else:
            st.info("No products assigned.")

    elif action == "Update Product Location":
        st.subheader("🛠️ Update Location")

        # Fetch products to create the dropdown for product ID
        products = view_products()  # Get the list of products
        if products:
            product_ids = [p['id'] for p in products]  # Extracting the product IDs for the dropdown
            product_id = st.selectbox("Select Product ID", product_ids)  # Dropdown to select the product ID

            # Once a product is selected, show the fields to enter new location and transport details
            if product_id:
                new_location = st.text_input("New Location")
                transport_details = st.text_area("Transport Details")

                if st.button("Update Location"):
                    if not all([new_location, transport_details]):
                        st.warning("Please fill in all fields.")
                    else:
                        result = add_distributor(product_id, new_location, transport_details)  # Replace with actual backend call
                        if result["success"]:
                            st.success("Location updated successfully!")
                        else:
                            st.error("Failed to update location.")
        else:
            st.info("No products found to update location.")

    elif action == "Product Trace View":
        st.subheader("📜 Product Trace View")

        product_id = st.text_input("Product ID")

        if st.button("View Trace"):
            if product_id:
                st.write(f"Trace for Product ID {product_id}:")
                # Mock trace data
                st.write("Origin: XYZ | Current Location: ABC | All roles involved")
            else:
                st.warning("Please provide a Product ID.")
