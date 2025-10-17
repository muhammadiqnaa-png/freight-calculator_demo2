# auth/firebase_auth.py
import requests
import streamlit as st

API_KEY = st.secrets.get("firebase_api_key")  # dari secrets.toml

FIREBASE_SIGNUP = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
FIREBASE_SIGNIN = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

def firebase_register(email: str, password: str):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(FIREBASE_SIGNUP, json=payload, timeout=10)
    return r

def firebase_login(email: str, password: str):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(FIREBASE_SIGNIN, json=payload, timeout=10)
    return r
