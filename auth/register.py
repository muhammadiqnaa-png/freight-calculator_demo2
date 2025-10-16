import streamlit as st
from auth.firebase_config import auth
from requests.exceptions import HTTPError

def register():
    st.title("🧾 Register Freight Calculator")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Daftar"):
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success("Akun berhasil dibuat ✅ Silakan login.")
            st.switch_page("auth/login.py")
        except HTTPError as e:
            error_json = e.response.json()
            error_message = error_json["error"]["message"]
            st.error(f"Gagal registrasi: {error_message}")

    st.write("---")
    st.write("Sudah punya akun?")
    if st.button("Login disini"):
        st.switch_page("auth/login.py")
