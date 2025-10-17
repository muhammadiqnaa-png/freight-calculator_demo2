import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import plotly.graph_objects as go

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# ===== SIDEBAR =====
st.sidebar.title("⚙️ Parameter (Bisa Diedit)")
mode = st.sidebar.selectbox("Select Mode", ["Owner", "Charter"])

# ===== SIDEBAR DENGAN EXPANDERS =====
if mode == "Owner":
    with st.sidebar.expander("Speed & Fuel", expanded=True):
        speed_laden = st.number_input("Speed Laden (knot)", 0.0)
        speed_ballast = st.number_input("Speed Ballast (knot)", 0.0)
        consumption = st.number_input("Consumption Fuel (liter)", 0)
        price_bunker = st.number_input("Price Bunker (Rp/liter)", 0)
        premi_nm = st.number_input("Premi (NM)", 0)

    with st.sidebar.expander("Fixed Cost", expanded=False):
        charter = st.number_input("Charter hire/Month (Rp)", 0)
        crew = st.number_input("Crew cost/Month (Rp)", 0)
        insurance = st.number_input("Insurance/Month (Rp)", 0)
        docking = st.number_input("Docking-Saving/Month (Rp)", 0)
        maintenance = st.number_input("Maintenance/Month (Rp)", 0)

    with st.sidebar.expander("Variable Cost", expanded=False):
        port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
        port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
        asist_tug = st.number_input("Asist Tug (Rp)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

    with st.sidebar.expander("Port Stay", expanded=False):
        port_stay_pol = st.number_input("Port Stay POL (Day)", 0)
        port_stay_pod = st.number_input("Port Stay POD (Day)", 0)

elif mode == "Charter":
    with st.sidebar.expander("Speed & Fuel", expanded=True):
        speed_laden = st.number_input("Speed Laden (knot)", 0.0)
        speed_ballast = st.number_input("Speed Ballast (knot)", 0.0)
        consumption = st.number_input("Consumption Fuel (liter)", 0)
        price_bunker = st.number_input("Price Bunker (Rp/liter)", 0)
        premi_nm = st.number_input("Premi (NM)", 0)

    with st.sidebar.expander("Fixed Cost", expanded=True):
        charter = st.number_input("Charter hire/Month (Rp)", 0)

    with st.sidebar.expander("Variable Cost", expanded=True):
        port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
        port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
        asist_tug = st.number_input("Asist Tug (Rp)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

# ===== MAIN PAGE INPUT =====
st.title("🚢 Freight Calculator Barge")

type_cargo = st.selectbox("Type Cargo", ["Pasir (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"])
qyt_cargo = st.number_input("QYT Cargo", 0.0)
pol_name = st.text_input("Port Of Loading", "POL")
pod_name = st.text_input("Port Of Discharge", "POD")
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0)
distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0)

# ===== HITUNG =====
if st.button("Hitung Freight Cost"):

    # VALIDASI INPUT
    if speed_laden <= 0 or speed_ballast <= 0:
        st.error("⚠️ Speed tidak boleh 0 atau negatif")
        st.stop()
    if qyt_cargo <= 0:
        st.error("⚠️ QYT Cargo harus lebih dari 0")
        st.stop()

    try:
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)

        if mode == "Owner":
            total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
            total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)

            charter_cost = (charter / 30) * total_voyage_days
            crew_cost = (crew / 30) * total_voyage_days
            insurance_cost = (insurance / 30) * total_voyage_days
            docking_cost = (docking / 30) * total_voyage_days
            maintenance_cost = (maintenance / 30) * total_voyage_days
            bunker_cost = total_consumption * price_bunker
            port_cost = port_cost_pol + port_cost_pod
            premi_cost = distance_pol_pod * premi_nm

            total_fixed_cost = charter_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost
            total_variable_cost = bunker_cost + port_cost + premi_cost + asist_tug + other_cost
            total_cost = total_fixed_cost + total_variable_cost

        else:  # Charter
            total_consumption = sailing_time * consumption
            bunker_cost = total_consumption * price_bunker
            port_cost = port_cost_pol + port_cost_pod
            premi_cost = distance_pol_pod * premi_nm

            total_fixed_cost = charter
            total_variable_cost = bunker_cost + port_cost + premi_cost + asist_tug + other_cost
            total_cost = total_fixed_cost + total_variable_cost

        freight_cost_per_unit = total_cost / qyt_cargo

        # ===== TAMPILKAN SEMUA ITEM =====
        st.subheader("📋 Hasil Perhitungan Lengkap")

        st.write(f"**Mode**: {mode}")
        st.write(f"**Port Loading**: {pol_name}")
        st.write(f"**Port Discharge**: {pod_name}")
        st.write(f"**Sailing Time (Hour)**: {sailing_time:,.2f}")

        if mode == "Owner":
            st.write(f"**Total Voyage Days**: {total_voyage_days:,.2f}")
            st.write(f"**Total Consumption (liter)**: {total_consumption:,.2f}")

        st.write("### Fixed Cost (Rp)")
        if mode == "Owner":
            st.write(f"Charter / Angsuran: Rp {charter_cost:,.2f}")
            st.write(f"Crew: Rp {crew_cost:,.2f}")
            st.write(f"Insurance: Rp {insurance_cost:,.2f}")
            st.write(f"Docking: Rp {docking_cost:,.2f}")
            st.write(f"Maintenance: Rp {maintenance_cost:,.2f}")
        else:
            st.write(f"Charter: Rp {charter:,.2f}")

        st.write("### Variable Cost (Rp)")
        st.write(f"Fuel / Bunker: Rp {bunker_cost:,.2f}")
        st.write(f"Port Cost POL: Rp {port_cost_pol:,.2f}")
        st.write(f"Port Cost POD: Rp {port_cost_pod:,.2f}")
        st.write(f"Premi: Rp {premi_cost:,.2f}")
        st.write(f"Asist Tug: Rp {asist_tug:,.2f}")
        st.write(f"Other Cost: Rp {other_cost:,.2f}")

        st.write(f"**Total Fixed Cost (Rp)**: {total_fixed_cost:,.2f}")
        st.write(f"**Total Variable Cost (Rp)**: {total_variable_cost:,.2f}")
        st.write(f"**Total Cost (Rp)**: {total_cost:,.2f}")
        st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]})**: {freight_cost_per_unit:,.2f}")

        # ===== PROFIT TABLE =====
        data = []
        for p in range(0, 55, 5):
            freight_with_profit = freight_cost_per_unit * (1 + p / 100)
            revenue = freight_with_profit * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"{freight_with_profit:,.2f}", f"{revenue:,.2f}", f"{pph:,.2f}", f"{profit:,.2f}"])

        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.subheader("📈 Tabel Profit 0% - 50%")
        st.dataframe(df_profit)

        # ===== GRAFIK FIXED vs VARIABLE COST =====
        cost_labels = []
        cost_values = []

        if mode == "Owner":
            cost_labels = ["Charter", "Crew", "Insurance", "Docking", "Maintenance",
                           "Fuel/Bunker", "Port POL", "Port POD", "Premi", "Asist Tug", "Other Cost"]
            cost_values = [charter_cost, crew_cost, insurance_cost, docking_cost, maintenance_cost,
                           bunker_cost, port_cost_pol, port_cost_pod, premi_cost, asist_tug, other_cost]
        else:
            cost_labels = ["Charter", "Fuel/Bunker", "Port POL", "Port POD", "Premi", "Asist Tug", "Other Cost"]
            cost_values = [charter, bunker_cost, port_cost_pol, port_cost_pod, premi_cost, asist_tug, other_cost]

        fig_cost = go.Figure(data=[go.Bar(x=cost_labels, y=cost_values, text=[f"Rp {v:,.0f}" for v in cost_values],
                                          textposition='auto')])
        fig_cost.update_layout(title="💰 Breakdown Fixed & Variable Cost", xaxis_title="Item", yaxis_title="Rp",
                               xaxis_tickangle=-45)
        st.plotly_chart(fig_cost, use_container_width=True)

        # ===== GRAFIK PROFIT vs PROFIT % =====
        profit_percent = [int(row[0][:-1]) for row in data]
        profit_values = [float(row[4].replace(",", "")) for row in data]

        fig_profit = go.Figure(data=[go.Scatter(x=profit_percent, y=profit_values, mode='lines+markers',
                                               text=[f"Rp {v:,.0f}" for v in profit_values], textposition="top center")])
        fig_profit.update_layout(title="📈 Profit vs Profit %", xaxis_title="Profit %", yaxis_title="Profit (Rp)")
        st.plotly_chart(fig_profit, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
