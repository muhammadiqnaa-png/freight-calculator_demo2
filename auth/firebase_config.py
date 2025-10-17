import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# Ambil credential dari Streamlit secrets
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)

# Fungsi login manual pakai email & password (opsional)
def sign_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        return user
    except Exception as e:
        st.error(f"Gagal login: {e}")
        return None
