import streamlit as st
import pandas as pd
from utils.pdf_generator import generate_pdf

def freight_page():
    st.title("🚢 Freight Calculator Barge")
    if "user" not in st.session_state or not st.session_state["user"]:
        st.warning("Silakan login terlebih dahulu.")
        st.stop()

    st.sidebar.header("⚙️ Parameter (Bisa Diedit)")

    # Sidebar parameters
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0)
    consumption = st.sidebar.number_input("Consumption Fuel (liter/jam)", 0.0)
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0.0)
    charter_hire = st.sidebar.number_input("Charter hire/Month (Rp)", 0.0)
    crew_cost = st.sidebar.number_input("Crew cost/Month (Rp)", 0.0)
    insurance = st.sidebar.number_input("Insurance/Month (Rp)", 0.0)
    docking = st.sidebar.number_input("Docking - Saving/Month (Rp)", 0.0)
    maintenance = st.sidebar.number_input("Maintenance/Month (Rp)", 0.0)
    port_pol = st.sidebar.number_input("Port Cost POL (Rp)", 0.0)
    port_pod = st.sidebar.number_input("Port Cost POD (Rp)", 0.0)
    tug = st.sidebar.number_input("Asist Tug (Rp)", 0.0)
    premi = st.sidebar.number_input("Premi (Rp/NM)", 0.0)
    other_cost = st.sidebar.number_input("Other Cost (Rp)", 0.0)
    port_stay_pol = st.sidebar.number_input("Port Stay POL (Day)", 0.0)
    port_stay_pod = st.sidebar.number_input("Port Stay POD (Day)", 0.0)

    st.sidebar.markdown("---")
    st.sidebar.header("📦 Input Utama")
    cargo_type = st.sidebar.selectbox("Type Cargo", ["Pasir (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"])
    qty_cargo = st.sidebar.number_input("QYT Cargo", 0.0)
    dist_pol_pod = st.sidebar.number_input("Distance POL - POD (NM)", 0.0)
    dist_pod_pol = st.sidebar.number_input("Distance POD - POL (NM)", 0.0)

    if st.button("Hitung Freight Cost"):
        # Perhitungan
        sailing_time = (dist_pol_pod / speed_laden) + (dist_pod_pol / speed_ballast) if speed_laden and speed_ballast else 0
        total_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)

        charter_cost = (charter_hire / 30) * total_days
        bunker_cost = total_consumption * price_bunker
        port_cost = port_pol + port_pod
        premi_cost = dist_pol_pod * premi
        crew_cost_total = (crew_cost / 30) * total_days
        insurance_cost = (insurance / 30) * total_days
        docking_cost = (docking / 30) * total_days
        maintenance_cost = (maintenance / 30) * total_days

        total_cost = charter_cost + bunker_cost + crew_cost_total + port_cost + premi_cost + tug + insurance_cost + docking_cost + maintenance_cost + other_cost
        freight_cost = total_cost / qty_cargo if qty_cargo else 0

        # Tabel Profit 0-50%
        profit_data = []
        for p in range(0, 55, 5):
            revenue = freight_cost * (1 + p / 100) * qty_cargo
            pph = revenue * 0.012
            profit = revenue - pph
            profit_data.append([f"{p}%", round(freight_cost * (1 + p / 100), 2), round(revenue, 2), round(pph, 2), round(profit, 2)])

        df = pd.DataFrame(profit_data, columns=["Profit %", "Freight (Rp/MT)", "Revenue (Rp)", "PPH 1.2%", "Profit (Rp)"])

        st.subheader("📊 Hasil Perhitungan")
        st.dataframe(df, use_container_width=True)

        pdf_bytes = generate_pdf(df, st.session_state["user"])
        st.download_button("📥 Download PDF", pdf_bytes, file_name="freight_calculation.pdf")

    st.markdown("---")
    st.caption(f"Generated Freight Calculator By {st.session_state['user']}")
