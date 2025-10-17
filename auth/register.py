import streamlit as st
import pyrebase

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

def register_page():
    st.title("📝 Daftar Akun Freight Calculator")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")

    if st.button("Daftar"):
        if password != confirm:
            st.warning("Password tidak cocok!")
        elif len(password) < 6:
            st.warning("Password minimal 6 karakter.")
        else:
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Akun berhasil dibuat! Silakan login.")
                st.session_state.show_register = False
                st.rerun()
            except Exception as e:
                st.error("Gagal registrasi. Mungkin email sudah terdaftar.")

    if st.button("Kembali ke Login"):
        st.session_state.show_register = False
        st.rerun()
