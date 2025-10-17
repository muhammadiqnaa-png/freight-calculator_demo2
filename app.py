import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# ===== SIDEBAR =====
st.sidebar.title("⚙️ Parameter (Bisa Diedit)")
mode = st.sidebar.selectbox("Select Mode", ["Owner", "Charter"])

# ===== PARAMETERS BASED ON MODE =====
if mode == "Owner":
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0)
    consumption = st.sidebar.number_input("Consumption Fuel (liter)", 0)
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0)
    charter = st.sidebar.number_input("Charter hire/Month (Rp)", 0)
    premi_nm = st.sidebar.number_input("Premi (NM)", 0)

    crew = st.sidebar.number_input("Crew cost/Month (Rp)", 0)
    insurance = st.sidebar.number_input("Insurance/Month (Rp)", 0)
    docking = st.sidebar.number_input("Docking-Saving/Month (Rp)", 0)
    maintenance = st.sidebar.number_input("Maintenance/Month (Rp)", 0)
    port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", 0)

    other_cost = st.sidebar.number_input("Other Cost (Rp)", 0)
    port_stay_pol = st.sidebar.number_input("Port Stay POL (Day)", 0)
    port_stay_pod = st.sidebar.number_input("Port Stay POD (Day)", 0)

elif mode == "Charter":
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0)
    consumption = st.sidebar.number_input("Consumption Fuel (liter)", 0)
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0)
    charter = st.sidebar.number_input("Charter hire/Month (Rp)", 0)
    premi_nm = st.sidebar.number_input("Premi (NM)", 0)

    port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", 0)
    other_cost = st.sidebar.number_input("Other Cost (Rp)", 0)

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
            bunker_cost = total_consumption * price_bunker
            port_cost = port_cost_pol + port_cost_pod
            premi_cost = distance_pol_pod * premi_nm
            crew_cost = (crew / 30) * total_voyage_days
            insurance_cost = (insurance / 30) * total_voyage_days
            docking_cost = (docking / 30) * total_voyage_days
            maintenance_cost = (maintenance / 30) * total_voyage_days

            total_cost = (
                charter_cost + bunker_cost + port_cost + premi_cost + crew_cost +
                asist_tug + insurance_cost + docking_cost + maintenance_cost + other_cost
            )
        else:  # Charter
            total_consumption = sailing_time * consumption
            bunker_cost = total_consumption * price_bunker
            port_cost = port_cost_pol + port_cost_pod
            premi_cost = distance_pol_pod * premi_nm

            total_cost = charter + bunker_cost + port_cost + premi_cost + asist_tug + other_cost

        freight_cost_per_unit = total_cost / qyt_cargo

        # ===== TAMPILKAN HASIL =====
        st.subheader("📋 Hasil Perhitungan")
        st.write(f"**Mode**: {mode}")
        st.write(f"**Port Loading**: {pol_name}")
        st.write(f"**Port Discharge**: {pod_name}")
        st.write(f"**Sailing Time (Hour)**: {sailing_time:,.2f}")
        if mode == "Owner":
            st.write(f"**Total Voyage Days**: {total_voyage_days:,.2f}")
            st.write(f"**Total Consumption (liter)**: {total_consumption:,.2f}")
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
        st.dataframe(df_profit)

        # ===== PDF GENERATOR =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("<b>Freight Calculator Barge</b>", styles['Title']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"<b>Mode: {mode}</b>", styles['Heading2']))
            elements.append(Paragraph(f"<b>Port Loading:</b> {pol_name}", styles['Normal']))
            elements.append(Paragraph(f"<b>Port Discharge:</b> {pod_name}", styles['Normal']))
            elements.append(Spacer(1, 12))

            # Parameter Table
            elements.append(Paragraph("<b>Parameter Input</b>", styles['Heading3']))
            if mode == "Owner":
                params = [
                    ["Speed Laden", f"{speed_laden} knot"],
                    ["Speed Ballast", f"{speed_ballast} knot"],
                    ["Consumption Fuel", f"{consumption} L"],
                    ["Price Bunker", f"Rp {price_bunker:,.0f}"],
                    ["Charter hire/Month", f"Rp {charter:,.0f}"],
                    ["Premi (NM)", f"Rp {premi_nm:,.0f}"],
                    ["Crew cost/Month", f"Rp {crew:,.0f}"],
                    ["Insurance/Month", f"Rp {insurance:,.0f}"],
                    ["Docking-Saving/Month", f"Rp {docking:,.0f}"],
                    ["Maintenance/Month", f"Rp {maintenance:,.0f}"],
                    ["Port Cost POL", f"Rp {port_cost_pol:,.0f}"],
                    ["Port Cost POD", f"Rp {port_cost_pod:,.0f}"],
                    ["Asist Tug", f"Rp {asist_tug:,.0f}"],
                    ["Other Cost", f"Rp {other_cost:,.0f}"],
                    ["Port Stay POL (Day)", f"{port_stay_pol}"],
                    ["Port Stay POD (Day)", f"{port_stay_pod}"]
                ]
            else:  # Charter
                params = [
                    ["Speed Laden", f"{speed_laden} knot"],
                    ["Speed Ballast", f"{speed_ballast} knot"],
                    ["Consumption Fuel", f"{consumption} L"],
                    ["Price Bunker", f"Rp {price_bunker:,.0f}"],
                    ["Charter hire/Month", f"Rp {charter:,.0f}"],
                    ["Premi (NM)", f"Rp {premi_nm:,.0f}"],
                    ["Port Cost POL", f"Rp {port_cost_pol:,.0f}"],
                    ["Port Cost POD", f"Rp {port_cost_pod:,.0f}"],
                    ["Asist Tug", f"Rp {asist_tug:,.0f}"],
                    ["Other Cost", f"Rp {other_cost:,.0f}"]
                ]

            t = Table(params, hAlign='LEFT')
            t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
            elements.append(t)
            elements.append(Spacer(1, 12))

            # Hasil Perhitungan
            elements.append(Paragraph("<b>Hasil Perhitungan</b>", styles['Heading3']))
            hasil = [["Sailing Time (Hour)", f"{sailing_time:,.2f}"]]
            if mode == "Owner":
                hasil += [["Total Voyage Days", f"{total_voyage_days:,.2f}"],
                          ["Total Consumption (liter)", f"{total_consumption:,.2f}"]]
            hasil += [["Total Cost (Rp)", f"{total_cost:,.2f}"],
                      [f"Freight Cost (Rp/{type_cargo.split()[1]})", f"{freight_cost_per_unit:,.2f}"]]

            t2 = Table(hasil, hAlign='LEFT')
            t2.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
            elements.append(t2)
            elements.append(Spacer(1, 12))

            # Tabel Profit
            elements.append(Paragraph("<b>Tabel Profit 0% - 50%</b>", styles['Heading3']))
            profit_table = [["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"]] + data
            t3 = Table(profit_table, hAlign='LEFT')
            t3.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.25, colors.black),
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
            ]))
            elements.append(t3)
