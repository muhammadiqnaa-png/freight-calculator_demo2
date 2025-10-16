import streamlit as st
import pyrebase
from .firebase_config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def login_page():
    st.title("🔑 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if email and password:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state["user"] = email
                    st.session_state.page = "freight"
                    st.success(f"Login sukses: {email}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login gagal: {e}")
            else:
                st.warning("Isi email dan password")
    with col2:
        if st.button("Register"):
            st.session_state.page = "register"
            st.rerun()
