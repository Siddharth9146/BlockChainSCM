import streamlit as st

# Initialize session state if not already initialized
def init_state():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'role' not in st.session_state:
        st.session_state['role'] = None
    if 'profile' not in st.session_state:
        st.session_state['profile'] = None  # Store user profile info (name, phone, etc.)
    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False  # Whether to show the signup page or not

# Set logged-in status and user role
def set_logged_in(status, role, profile):
    st.session_state['logged_in'] = status
    st.session_state['role'] = role
    st.session_state['profile'] = profile

# Reset session state on logout
def logout():
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['profile'] = None

# Check if user is logged in
def is_logged_in():
    return st.session_state['logged_in']

# Set whether to show signup page
def show_signup(value):
    st.session_state['show_signup'] = value
