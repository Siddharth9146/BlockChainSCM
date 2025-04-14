import streamlit as st
import requests
from producer import producer_ui  # Import the producer_ui function
from consumer import consumer_ui  # Import the consumer_ui function

API_URL = "http://127.0.0.1:8000"  # Make sure the API URL is correct

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Call the backend login API
        response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})

        # Debugging: Check if we got a response
        st.write("Response status code:", response.status_code)
        st.write("Response data:", response.json())

        if response.status_code == 200:
            response_data = response.json()
            st.write(response_data)  # Show the full response for debugging

            if response_data.get("success"):
                # Parse the necessary info
                user_id = response_data.get("user_id")
                role = response_data.get("role")
                username = response_data.get("username")

                # Store necessary information in session state
                st.session_state["user_id"] = user_id
                st.session_state["role"] = role
                st.session_state["username"] = username
                st.session_state["login_success"] = True  # Mark login as successful

                st.success(f"Logged in successfully as {username}!")  # Show login success message

                # Rerun the app to show role-specific page
                st.rerun()  # Force a rerun to display the role-specific page
            else:
                st.error("Login failed. Invalid username or password.")
        else:
            st.error("Login failed. Server error.")

def producer_page():
    producer_ui()  # Display producer UI

def consumer_page():
    consumer_ui()  # Display consumer UI

# Define functions for other roles (distributor_page, retailer_page, etc.)
def distributor_page():
    st.write("Distributor Page Placeholder")

def retailer_page():
    st.write("Retailer Page Placeholder")

def regulator_page():
    st.write("Regulator Page Placeholder")

def display_role_page():
    # Debugging: Confirm if this function is being called
    st.write("### Debug: In display_role_page()")

    role = st.session_state.get("role")
    st.write(f"Session state: {st.session_state}")  # Show session state for debugging

    if role == "producer":
        producer_page()  # Show producer page
    elif role == "consumer":
        consumer_page()  # Show consumer page
    elif role == "distributor":
        distributor_page()  # Show distributor page
    elif role == "retailer":
        retailer_page()  # Show retailer page
    elif role == "regulator":
        regulator_page()  # Show regulator page
    else:
        st.error("Unknown role")

def main():
    # Debugging: Check session state and flow
    st.write("### Debug: In main()")
    st.write(f"Session state before check: {st.session_state}")  # Show session state for debugging

    if "login_success" in st.session_state and st.session_state["login_success"]:
        # If user is logged in, show the role-specific page
        st.write("login success processing in main")
        display_role_page()
    else:
        # If not logged in, show the login page
        login()

if __name__ == "__main__":
    main()
# Sign Up Function
def signup():
    st.title("📝 Sign Up")

    username = st.text_input("Username")  # 1. username
    password = st.text_input("Password", type="password")  # 2. password
    role = st.selectbox("Role", ["producer", "distributor", "retailer", "consumer", "regulator"])  # 3. role
    phone = st.text_input("Phone Number")  # 4. phone
    email = st.text_input("Email")  # 5. email

    if st.button("Register"):
        if not username or not password or not role or not phone or not email:
            st.warning("Please fill all the fields.")
            return

        payload = {
            "username": username,
            "password": password,
            "role": role,
            "phone": phone,
            "email": email
        }

        response = requests.post(f"{API_URL}/register", json=payload)
        if response.status_code == 201:
            st.success("✅ User registered successfully. Please login.")
        else:
            try:
                st.error(f"❌ {response.json().get('detail', 'Registration failed.')}")
            except Exception:
                st.error("❌ Registration failed. Invalid server response.")