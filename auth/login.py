import streamlit as st
from auth.firebase_config import auth
from utils.footer import show_footer

def login_page():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state["user"] = user
            st.session_state["email"] = email
            st.success("Login berhasil ✅")
            st.rerun()
        except Exception as e:
            st.error("Email atau password salah!")

    st.markdown("Belum punya akun? [Daftar di sini](#)")
    show_footer(st.session_state.get("email"))
