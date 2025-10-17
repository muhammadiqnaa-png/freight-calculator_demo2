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
    st.title("🔐 Login Freight Calculator")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state["user"] = email
            st.success("Login berhasil!")
            st.switch_page("pages/freight_calculator.py")
        except Exception as e:
            st.error(f"Gagal login: {e}")

    st.write("Belum punya akun? [Daftar di sini](register.py)")
