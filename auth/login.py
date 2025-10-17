import streamlit as st
from firebase.firebase_config import auth, db

def login_page():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.get_user_by_email(email)
            st.success(f"Berhasil login sebagai {email}")
            return True
        except:
            st.error("Email atau password salah")
            return False
