import sys, os
import streamlit as st

# Pastikan folder bisa diakses
sys.path.append(os.path.dirname(__file__))

from auth.login import login_page
from pages.freight_calculator import freight_page

st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# Simpan session login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if not st.session_state.logged_in:
    login_page()
else:
    freight_page()
