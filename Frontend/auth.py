
import streamlit as st
from utils import send_post

def login_section():
    login_mode = st.radio("Choose Option", ["Login", "Register"])

    with st.form(key="auth_form"):
        name, phone = "", ""
        if login_mode == "Register":
            name = st.text_input("Name")
            phone = st.text_input("Phone")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Submit")

        if submit:
            if login_mode == "Register":
                payload = {"name": name, "email": email, "password": password, "phone": phone, "role": st.session_state.role}
                res = send_post("/register", payload)
                if res.get("status") == "success":
                    st.success("Registered successfully! You can now login.")
                else:
                    st.error(res.get("error", "Registration failed"))
            else:
                payload = {"email": email, "password": password, "role": st.session_state.role}
                res = send_post("/login", payload)
                if res.get("authenticated"):
                    st.session_state["authenticated"] = True
                    st.session_state["name"] = res["name"]
                    st.session_state["email"] = email
                    st.success("Login successful!")
                else:
                    st.error("Login failed. Try again.")
