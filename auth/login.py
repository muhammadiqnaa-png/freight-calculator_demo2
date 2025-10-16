import streamlit as st
from auth.firebase_config import auth
from requests.exceptions import HTTPError

def login():
    st.title("🔐 Login Freight Calculator")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state["user"] = user
            st.success("Login berhasil ✅")
            st.switch_page("pages/freight_calculator.py")
        except HTTPError as e:
            error_json = e.response.json()
            error_message = error_json["error"]["message"]
            st.error(f"Gagal login: {error_message}")

    st.write("---")
    st.write("Belum punya akun?")
    if st.button("Daftar disini"):
        st.switch_page("auth/register.py")
