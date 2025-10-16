import streamlit as st

def freight_page():
    st.title("⚓ Freight Calculator Barge")
    st.write("Selamat datang,", st.session_state.get("user", "User"))

    st.sidebar.header("Parameter (Bisa Diedit)")

    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0)
    consumption = st.sidebar.number_input("Consumption Fuel (liter)", 0)
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0)
    charter_hire = st.sidebar.number_input("Charter hire/Month (Rp)", 0)

    st.write("🚀 Halaman Kalkulator dalam tahap pengembangan.")

    st.write("---")
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.page = "login"
        st.rerun()
