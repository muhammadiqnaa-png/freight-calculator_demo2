import streamlit as st
from auth.firebase_config import auth

def register_page():
    st.title("📝 Daftar Akun Baru")

    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Daftar")

    if submit:
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success("Akun berhasil dibuat! Silakan login.")
            st.session_state.show_register = False
            st.rerun()
        except Exception as e:
            st.error("Gagal membuat akun. Pastikan password minimal 6 karakter.")
