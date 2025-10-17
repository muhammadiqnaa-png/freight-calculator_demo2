import streamlit as st
from auth.login import login_page

def main():
    if "user" not in st.session_state:
        login_page()
    else:
        st.switch_page("pages/freight_calculator.py")

if __name__ == "__main__":
    main()
