import streamlit as st

st.set_page_config(page_title="Freight Calculator Barge", page_icon="⚓", layout="wide")

# --- Redirect sederhana tanpa switch_page() ---
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    from auth.login import login_page
    login_page()

elif st.session_state.page == "register":
    from auth.register import register_page
    register_page()

elif st.session_state.page == "freight":
    from pages.freight_calculator import freight_page
    freight_page()
