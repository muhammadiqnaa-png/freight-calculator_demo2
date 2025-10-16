import streamlit as st

def register_page():
    st.title("📝 Register Akun")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")

    if st.button("Daftar"):
        if password != confirm:
            st.error("Password tidak cocok!")
        elif len(password) < 6:
            st.error("Password minimal 6 karakter!")
        else:
            st.success("Akun berhasil dibuat! Silakan login.")
            st.session_state.page = "login"
            st.experimental_rerun()

    st.write("---")
    if st.button("Sudah punya akun? Login di sini"):
        st.session_state.page = "login"
        st.experimental_rerun()
