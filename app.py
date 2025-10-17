import streamlit as st
from auth.login import login_page
from auth.register import register_page
from calculations.freight_calc import calculate_freight
from utils.pdf_generator import generate_pdf
import pandas as pd

st.set_page_config(page_title="Freight Calculator Barge")

# Auth
auth_choice = st.sidebar.selectbox("Login/Register", ["Login","Register"])
if auth_choice=="Register":
    register_page()
else:
    logged_in = login_page()
    if not logged_in:
        st.stop()

# Mode Owner / Charter
mode = st.radio("Mode", ["Owner","Charter"])

# Input Utama
st.header("Input Utama")
port_pol = st.text_input("Port Of Loading")
port_pod = st.text_input("Port Of Discharge")
cargo_type = st.selectbox("Type Cargo", ["Pasir (M3)","Split (MT)","Coal (MT)","Nickel (MT)"])
qty_cargo = st.number_input("QTY Cargo", value=0.0)
distance_pol_pod = st.number_input("Distance POL - POD (NM)", value=0.0)
distance_pod_pol = st.number_input("Distance POD - POL (NM)", value=0.0)

# Sidebar Parameter
st.sidebar.header("Parameter")
speed_laden = st.sidebar.number_input("Speed Laden (knot)", value=0.0)
speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", value=0.0)
consumption_fuel = st.sidebar.number_input("Consumption Fuel (liter)", value=0.0)
price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", value=0.0)
charter_hire = st.sidebar.number_input("Charter Hire/Month (Rp)", value=0.0)
crew_cost = st.sidebar.number_input("Crew cost/Month (Rp)", value=0.0)
insurance = st.sidebar.number_input("Insurance/Month (Rp)", value=0.0)
docking = st.sidebar.number_input("Docking-Saving/Month (Rp)", value=0.0)
maintenance = st.sidebar.number_input("Maintenance/Month (Rp)", value=0.0)
port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", value=0.0)
port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", value=0.0)
asist_tug = st.sidebar.number_input("Asist Tug (Rp)", value=0.0)
premi = st.sidebar.number_input("Premi (NM)", value=0.0)
port_stay_pol = st.sidebar.number_input("Port Stay POL (Day)", value=0.0)
port_stay_pod = st.sidebar.number_input("Port Stay POD (Day)", value=0.0)
other_cost = st.sidebar.number_input("Other Cost (Rp)", value=0.0)

params = {
    "speed_laden": speed_laden,
    "speed_ballast": speed_ballast,
    "consumption_fuel": consumption_fuel,
    "price_bunker": price_bunker,
    "charter_hire": charter_hire,
    "crew_cost": crew_cost,
    "insurance": insurance,
    "docking": docking,
    "maintenance": maintenance,
    "port_cost_pol": port_cost_pol,
    "port_cost_pod": port_cost_pod,
    "asist_tug": asist_tug,
    "premi": premi,
    "port_stay_pol": port_stay_pol,
    "port_stay_pod": port_stay_pod,
    "other_cost": other_cost,
    "qty_cargo": qty_cargo,
    "distance_pol_pod": distance_pol_pod,
    "distance_pod_pol": distance_pod_pol
}

if st.button("Hitung"):
    results = calculate_freight(params, mode=mode)
    st.success(f"Total Cost: Rp {results['total_cost']:.2f}")
    st.success(f"Freight per Unit: Rp {results['freight_per_unit']:.2f}")

    st.subheader("Profit Table 0-50%")
    df_profit = pd.DataFrame(results['profit_table'])
    st.dataframe(df_profit)

    pdf_file = generate_pdf(results)
    st.download_button("Download PDF", pdf_file, file_name="freight_result.pdf")

