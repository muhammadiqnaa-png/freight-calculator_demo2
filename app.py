import streamlit as st
from auth.login import login_page
from auth.register import register_page
from pages.freight_calculator import freight_page

st.set_page_config(page_title="Freight Calculator", layout="centered")

if "user" not in st.session_state:
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["page"] == "login":
        login_page()
        st.markdown(
            '<a href="#" onclick="window.location.reload()">Daftar Akun</a>',
            unsafe_allow_html=True
        )
    elif st.session_state["page"] == "register":
        register_page()

else:
    freight_page()
