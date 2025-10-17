import streamlit as st
from auth.firebase_config import auth
from auth.register import register_page

def login_page():
    st.title("🔐 Login ke Freight Calculator")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("Login berhasil!")
            st.rerun()
        except Exception as e:
            st.error("Gagal login. Periksa email dan password.")

    st.markdown("---")
    st.write("Belum punya akun?")
    if st.button("Daftar di sini"):
        st.session_state.show_register = True
        st.rerun()

    if "show_register" in st.session_state and st.session_state.show_register:
        register_page()
