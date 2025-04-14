import streamlit as st
from auth import login, signup
from producer import producer_ui
from distributor import distributor_ui
from retailer import retailer_ui
from consumer import consumer_ui
from regulator import regulator_ui

st.set_page_config(page_title="Supply Chain Frontend", layout="wide")

if "token" not in st.session_state:
    menu = st.sidebar.selectbox("Choose", ["Login", "Sign Up"])
    if menu == "Login":
        login()
    else:
        signup()
else:
    role = st.sidebar.selectbox("Role", ["producer", "distributor", "retailer", "consumer", "regulator"])
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

    if role == "producer":
        producer_ui(st.session_state["token"])
    elif role == "distributor":
        distributor_ui(st.session_state["token"])
    elif role == "retailer":
        retailer_ui(st.session_state["token"])
    elif role == "consumer":
        consumer_ui(st.session_state["token"])
    elif role == "regulator":
        regulator_ui(st.session_state["token"])
