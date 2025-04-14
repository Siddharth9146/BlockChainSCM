import streamlit as st
import json

# Dummy function to save registration info
def save_user(username, password, role):
    # For testing purposes, save it in a dummy way (ideally, this would be saved in a database)
    with open("users.json", "a") as f:
        user_data = {
            "username": username,
            "password": password,
            "role": role
        }
        json.dump(user_data, f)
        f.write("\n")

def signup_ui():
    st.title("Sign Up Page")
    
    # Registration form fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.selectbox("Select Your Role", ["Producer", "Distributor", "Retailer", "Consumer"])
    
    if st.button("Register"):
        # Check if passwords match
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif username and password and role:
            save_user(username, password, role)
            st.success(f"Registration successful! You are a {role}.")
        else:
            st.error("Please fill in all fields.")
