import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# Load konfigurasi dari secrets.toml
firebase_config = st.secrets["firebase"]

# Inisialisasi Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

def sign_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        return user
    except Exception as e:
        st.error(f"Login gagal: {e}")
        return None
