import streamlit as st
from signup import signup_ui
from producer import producer_ui
from distributor import distributor_ui
from retailer import retailer_ui
from consumer import consumer_ui
from regulator import regulator_ui
# Dummy data for login validation
dummy_users = {
    "1": {"password": "1", "role": "Producer"},
    "2": {"password": "2", "role": "Distributor"},
    "3": {"password": "3", "role": "Retailer"},
    "4": {"password": "4", "role": "Consumer"},
    "5": {"password": "5", "role": "Regulator"}
}

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "login"  # can be "login" or "signup"

def login_ui():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in dummy_users and dummy_users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = dummy_users[username]["role"]
            st.success(f"Login successful! You are logged in as a {st.session_state.role}.")
        else:
            st.error("Invalid username or password.")

    st.markdown("Don't have an account?")
    if st.button("Go to Signup"):
        st.session_state.page = "signup"

# Retailer signup UI
def retailer_signup_ui():
    st.title("Retailer Signup")

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if password != confirm_password:
        st.warning("Passwords do not match!")

    if st.button("Sign Up"):
        if username and password:
            # Add the user to the dummy database with "Retailer" role
            dummy_users[username] = {"password": password, "role": "Retailer"}
            st.success("Signup successful! You can now log in.")
            st.session_state.page = "login"
        else:
            st.warning("Please fill in all the fields.")

# Role-based UI for Retailer
def display_role_ui():
    if st.session_state.role == "Producer":
        producer_ui()
    elif st.session_state.role == "Distributor":
        distributor_ui()
    elif st.session_state.role == "Retailer":
        retailer_ui()
    elif st.session_state.role == "Consumer":
        consumer_ui()
    elif st.session_state.role == "Regulator":
        regulator_ui()

# Main logic
if st.session_state.page == "signup":
    retailer_signup_ui()
    if st.button("Back to Login"):
        st.session_state.page = "login"

elif st.session_state.logged_in:
    display_role_ui()
else:
    login_ui()
