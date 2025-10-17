import streamlit as st

def show_footer(user_email=None):
    st.markdown("---")
    if user_email:
        st.markdown(
            f"<p style='text-align:center;font-size:13px;color:gray;'>"
            f"Generated Freight Calculator by <b>{user_email}</b>"
            f"</p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<p style='text-align:center;font-size:13px;color:gray;'>"
            "Generated Freight Calculator by Iqna</p>",
            unsafe_allow_html=True,
        )
