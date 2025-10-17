import streamlit as st
from auth.firebase_config import sign_in

def login_page():
    st.title("🚛 Freight Calculator Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = sign_in(email, password)
        if user:
            st.session_state["user"] = user.email
            st.success(f"Selamat datang, {user.email}!")
            st.switch_page("pages/freight_calculator.py")
