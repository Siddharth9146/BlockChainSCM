import streamlit as st
import requests

API_URL = "http://localhost:8000"

def login_ui():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state.token = token
                # Fetch user info
                user_info = requests.get(f"{API_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
                if user_info.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.role = user_info.json().get("role")
                    st.success(f"Logged in as {st.session_state.role}")
                else:
                    st.error("Failed to retrieve user information.")
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter both username and password.")

    st.markdown("Don't have an account?")
    if st.button("Go to Signup"):
        st.session_state.page = "signup"
