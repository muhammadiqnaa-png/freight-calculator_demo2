import streamlit as st

st.set_page_config(page_title="Freight Calculator Barge", page_icon="⚓", layout="wide")

# Kalau user belum login, arahkan ke halaman login
if "user" not in st.session_state:
    st.switch_page("auth/login.py")
else:
    st.switch_page("pages/freight_calculator.py")
