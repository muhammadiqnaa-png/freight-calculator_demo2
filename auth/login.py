import streamlit as st
import pyrebase4 as pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDRxbw6-kJQsXXXr0vpnlDqhaUWKOjmQIU",
    "authDomain": "freight-demo2.firebaseapp.com",
    "projectId": "freight-demo2",
    "storageBucket": "freight-demo2.appspot.com",
    "messagingSenderId": "199645170835",
    "appId": "1:199645170835:web:efa8ff8d5b85416eb71166",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def login_page():
    st.title("🔐 Login Freight Calculator Barge")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.logged_in = True
            st.session_state.user = email.split("@")[0]  # ambil nama depan dari email
            st.rerun()
        except Exception as e:
            st.error("Login gagal! Periksa email/password kamu.")

    st.markdown("---")
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state.show_register = True
        st.rerun()
