import firebase_admin
from firebase_admin import credentials, auth

# Gunakan file kredensial Firebase (service account)
# atau langsung dari secrets.toml biar aman
import streamlit as st

if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "freight-demo2",
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)
