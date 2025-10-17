import streamlit as st
from utils.footer import show_footer

def freight_page():
    st.title("📦 Freight Calculator")

    user_email = st.session_state.get("email", "User")

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Berat (kg)", min_value=0.0)
    with col2:
        distance = st.number_input("Jarak (km)", min_value=0.0)

    if st.button("Hitung"):
        cost = weight * distance * 1500  # contoh formula
        st.success(f"Total biaya: Rp {cost:,.0f}")

    st.write("---")
    st.button("Logout", on_click=lambda: logout())
    show_footer(user_email)

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Berhasil logout.")
    st.rerun()
