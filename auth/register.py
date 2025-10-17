import streamlit as st
from auth.firebase_config import auth
from utils.footer import show_footer

def register_page():
    st.title("📝 Daftar Akun")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")

    if st.button("Daftar"):
        if password != confirm:
            st.error("Password tidak cocok!")
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("Akun berhasil dibuat ✅ Silakan login.")
                st.session_state["page"] = "login"
                st.rerun()
            except Exception:
                st.error("Gagal membuat akun. Mungkin email sudah digunakan.")

    st.markdown("Sudah punya akun? [Login di sini](#)")
    show_footer(None)
