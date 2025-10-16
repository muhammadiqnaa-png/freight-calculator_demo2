import streamlit as st
import pyrebase
from firebase_config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def register_page():
    st.title("📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if email and password:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("Register sukses, silakan login!")
                st.session_state.page = "login"
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Register gagal: {e}")
        else:
            st.warning("Isi email dan password")
