import streamlit as st

def login_page():
    st.title("🔐 Login Freight Calculator")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # sementara login dummy
        if email == "admin@gmail.com" and password == "123456":
            st.session_state["user"] = email
            st.session_state.page = "freight"
            st.rerun()
        else:
            st.error("Email atau password salah!")

    st.write("---")
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state.page = "register"
        st.rerun()
