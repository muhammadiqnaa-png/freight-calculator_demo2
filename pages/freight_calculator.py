import streamlit as st
from utils.calculations import calculate_freight
from utils.pdf_generator import generate_pdf
from utils.footer import footer

def freight_page():
    st.title("⚓ Freight Calculator Barge")

    st.sidebar.header("Parameter (Bisa Diedit)")
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", value=0.0)
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", value=0.0)
    fuel_consumption = st.sidebar.number_input("Consumption Fuel (liter/jam)", value=0)
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", value=0)
    charter_hire = st.sidebar.number_input("Charter hire/Month (Rp)", value=0)
    crew_cost = st.sidebar.number_input("Crew cost/Month (Rp)", value=0)
    insurance = st.sidebar.number_input("Insurance/Month (Rp)", value=0)
    docking = st.sidebar.number_input("Docking - Saving/Month (Rp)", value=0)
    maintenance = st.sidebar.number_input("Maintenance/Month (Rp)", value=0)
    port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", value=0)
    port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", value=0)
    assist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=0)
    premi = st.sidebar.number_input("Premi (Rp/NM)", value=0)
    other_cost = st.sidebar.number_input("Other Cost (Rp)", value=0)
    port_stay_pol = st.sidebar.number_input("Port Stay POL (Day)", value=0)
    port_stay_pod = st.sidebar.number_input("Port Stay POD (Day)", value=0)

    st.header("📦 Input Utama")
    cargo_type = st.selectbox("Type Cargo", ["Pasir (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"])
    cargo_qty = st.number_input("QTY Cargo", value=0)
    dist_pol_pod = st.number_input("Distance POL - POD (NM)", value=0)
    dist_pod_pol = st.number_input("Distance POD - POL (NM)", value=0)

    if st.button("🔍 Hitung Freight"):
        results, profit_table = calculate_freight(
            speed_laden, speed_ballast, fuel_consumption, price_bunker,
            charter_hire, crew_cost, insurance, docking, maintenance,
            port_cost_pol, port_cost_pod, assist_tug, premi, other_cost,
            port_stay_pol, port_stay_pod, cargo_type, cargo_qty, dist_pol_pod, dist_pod_pol
        )

        st.success("✅ Perhitungan Selesai!")
        st.dataframe(results)
        st.write("📊 Tabel Profit 0% - 50%")
        st.dataframe(profit_table)

        pdf = generate_pdf(results, profit_table, st.session_state.user_email)
        st.download_button("📥 Download Hasil (PDF)", data=pdf, file_name="Freight_Result.pdf", mime="application/pdf")

    footer(st.session_state.user_email)
