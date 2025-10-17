import streamlit as st
from auth.login import login_page
from auth.register import register_page
from pages.freight_calculator import freight_page

st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# Session default
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# Routing manual
if not st.session_state.logged_in:
    if st.session_state.show_register:
        register_page()
    else:
        login_page()
else:
    freight_page()
