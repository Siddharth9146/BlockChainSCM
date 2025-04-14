import streamlit as st
import requests
from requests.exceptions import JSONDecodeError

API_URL = "http://localhost:8000"  # Adjust to your FastAPI server

def signup():
    st.title("🔐 Sign Up")

    with st.form("signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Select Role", ["Producer", "Distributor", "Retailer", "Consumer", "Regulator"])
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        submit_btn = st.form_submit_button("Sign Up")

    if submit_btn:
        if not username or not password or not email:
            st.warning("Username, email, and password are required.")
            return

        payload = {
            "username": username,
            "password": password,
            "role": role.lower(),
            "phone": phone,
            "email": email
        }

        try:
            response = requests.post(f"{API_URL}/register", json=payload)
            st.text(f"DEBUG: {response.status_code} - {response.text}")

            if response.status_code == 201:
                try:
                    res_json = response.json()
                    st.success(f"✅ {res_json.get('message', 'Account created successfully.')}")
                    st.info(f"🆔 User ID: {res_json.get('user_id')}")
                except JSONDecodeError:
                    st.success("✅ Account created successfully (no JSON response).")
            elif response.status_code == 400:
                try:
                    error_detail = response.json().get("detail", "Bad request.")
                except JSONDecodeError:
                    error_detail = response.text or "Bad request with no JSON body."
                st.error(f"❌ {error_detail}")
            else:
                try:
                    error_detail = response.json().get("detail", response.text)
                except JSONDecodeError:
                    error_detail = response.text or "Unexpected server error."
                st.error(f"⚠️ {response.status_code} - {error_detail}")

        except requests.exceptions.ConnectionError:
            st.error("🚫 Could not connect to the backend. Make sure FastAPI is running.")

if __name__ == "__main__":
    signup()
    