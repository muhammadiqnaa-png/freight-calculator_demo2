import streamlit as st

def footer(user):
    st.markdown("---")
    st.markdown(
        f"<p style='text-align:center; font-size:12px;'>Generated Freight Calculator by <b>{user}</b></p>",
        unsafe_allow_html=True
    )
