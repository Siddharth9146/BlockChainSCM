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
                token = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                token_data = token.json()

                if token.status_code != 200:
                    st.error("Failed to retrieve access token.")
                    return
                
               
                st.write("Token status code:", token.status_code)
                st.write("Token data:", token_data)  # Show the full token response for debugging
                # Check if token retrieval was successful
                if "access_token" not in token_data:
                    st.error("Failed to retrieve access token.")
                    return
                # Extract user information


                user_id = response_data.get("user_id")
                access_token = response_data.get("access_token")
                role = response_data.get("role")
                access_token = token_data.get("access_token")
                username = response_data.get("username")

                # Store necessary information in session state
                st.session_state["access_token"] = access_token
                st.session_state["user_id"] = user_id
                st.session_state["role"] = role
                st.session_state["username"] = username
                st.session_state["login_success"] = True  # Mark login as successful
                st.session_state["access_token"] = access_token # Store access token
                st.success(f"Logged in successfully as {username}!")  # Show login success message

                # Rerun the app to show role-specific page
                # st.rerun()  # Force a rerun to display the role-specific page
            else:
                st.error("Login failed. Invalid username or password.")
        else:
            st.error("Login failed. Server error.")

    if st.button("Dont have an account? Sign Up"):
        st.session_state["show_signup"] = True

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
                
    if st.button("Already have an account? Login"):
        st.session_state["show_signup"] = False
        


def main():
    st.write("### Debug: In main()")
    if "show_signup" not in st.session_state:
        st.session_state["show_signup"] = False

    if st.session_state.get("login_success"):
        st.write("### Debug: Login success detected in main()")
        display_role_page()
    elif st.session_state["show_signup"]:
        signup()
    else:
        login()



if __name__ == "__main__":
    main()