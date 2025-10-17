import streamlit as st
from firebase.firebase_config import auth, db

def register_page():
    st.title("Daftar Akun")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    username = st.text_input("Username")

    if st.button("Daftar"):
        try:
            user = auth.create_user(email=email, password=password)
            db.collection("users").document(user.uid).set({"username": username, "email": email})
            st.success("Akun berhasil dibuat!")
        except Exception as e:
            st.error(f"Error: {e}")
