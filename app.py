import streamlit as st
import math
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import requests

st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# ====== FIREBASE AUTH (pakai secrets.toml) ======
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
REGISTER_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

def login_user(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

def register_user(email, password):
    res = requests.post(REGISTER_URL, json={"email": email, "password": password, "returnSecureToken": True})
    return res.ok, res.json()

# ===== LOGIN PAGE =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>🔐 Freight Calculator Login</h2>", unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login 🚀"):
            ok, data = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password!")

    with tab_register:
        email_reg = st.text_input("Register Email")
        password_reg = st.text_input("Register Password", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(email_reg, password_reg)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                st.error("Registration failed. Email may already be registered.")
    st.stop()

# ===== MAIN APP =====
# Sidebar - Logout
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Successfully logged out.")
    st.rerun()

st.sidebar.title("⚙️ Calculation Parameters")
mode = st.sidebar.radio("Operation Mode", ["Owner", "Charter"])

# Sidebar Expander Groups
with st.sidebar.expander("🚢 Speed"):
    speed_laden = st.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("🌊 Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel"):
    consumption_fuel = st.number_input("Consumption Fuel (liter/hour)", 0)
    price_fuel = st.number_input("Price Fuel (Rp/liter)", 0)

with st.sidebar.expander("💧 Freshwater"):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/day)", 0)
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0)

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        charter = st.number_input("Installment (Rp/Month)", 0)
        crew = st.number_input("Crew (Rp/Month)", 0)
        insurance = st.number_input("Insurance (Rp/Month)", 0)
        docking = st.number_input("Docking (Rp/Month)", 0)
        maintenance = st.number_input("Maintenance (Rp/Month)", 0)
        certificate = st.number_input("Certificate (Rp/Month)", 0)
        premi = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        charter = st.number_input("Charter Hire (Rp/Month)", 0)
        premi = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

with st.sidebar.expander("⚓ Port Cost"):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.number_input("Asist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay"):
    port_stay_pol = st.number_input("POL (Days)", 0)
    port_stay_pod = st.number_input("POD (Days)", 0)

# ===== Main Inputs =====
st.title("🚢 Freight Calculator Barge")

col1, col2 = st.columns(2)
with col1:
    port_pol = st.text_input("Port Of Loading")
with col2:
    port_pod = st.text_input("Port Of Discharge")

type_cargo = st.selectbox("Cargo Type", ["Sand (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"])
qyt_cargo = st.number_input("Cargo Quantity", 0.0)
distance_pol_pod = st.number_input("Distance POL-POD (NM)", 0.0)
distance_pod_pol = st.number_input("Distance POD-POL (NM)", 0.0)

# ===== Calculation =====
if st.button("Calculate Freight 💸"):
    try:
        # Time & consumption
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_rounded = round(total_voyage_days)
        total_consumption_fuel = (sailing_time * consumption_fuel) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_rounded

        # Cost calculation
        bunker_cost = total_consumption_fuel * price_fuel
        freshwater_cost = total_consumption_fw * price_fw
        charter_cost = (charter / 30) * total_voyage_days if mode=="Owner" else (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode=="Owner" else 0
        premi_cost = distance_pol_pod * premi
        port_cost = port_cost_pol + port_cost_pod + asist_tug

        total_cost = (
            bunker_cost + freshwater_cost + charter_cost + crew_cost + insurance_cost +
            docking_cost + maintenance_cost + certificate_cost + premi_cost + port_cost + other_cost
        )

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # Profit scenario
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"{freight_persen:,.2f}", f"{revenue:,.2f}", f"{pph:,.2f}", f"{profit:,.2f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])

        # ===== Display Main Calculation Results =====
        with st.expander("📋 Freight Calculation Result", expanded=True):
            st.subheader("🚢 Voyage & Consumption")
            st.write(f"**Total Voyage Days:** {total_voyage_days:,.2f}")
            st.write(f"**Sailing Time (Hour):** {sailing_time:,.2f}")
            st.write(f"**Fuel Consumption (liter):** {total_consumption_fuel:,.2f}")
            st.write(f"**Freshwater Consumption (Ton):** {total_consumption_fw:,.2f}")

            st.subheader("💰 Costs")
            st.write(f"**Bunker Cost (Rp):** {bunker_cost:,.2f}")
            st.write(f"**Freshwater Cost (Rp):** {freshwater_cost:,.2f}")
            st.write(f"**Charter/Installment Cost (Rp):** {charter_cost:,.2f}")
            if mode=="Owner":
                st.write(f"**Crew Cost (Rp):** {crew_cost:,.2f}")
                st.write(f"**Insurance Cost (Rp):** {insurance_cost:,.2f}")
                st.write(f"**Docking Cost (Rp):** {docking_cost:,.2f}")
                st.write(f"**Maintenance Cost (Rp):** {maintenance_cost:,.2f}")
                st.write(f"**Certificate Cost (Rp):** {certificate_cost:,.2f}")
            st.write(f"**Premi Cost (Rp):** {premi_cost:,.2f}")
            st.write(f"**Port Costs (Rp):** {port_cost:,.2f}")
            st.write(f"**Other Cost (Rp):** {other_cost:,.2f}")

            st.subheader("💵 Total")
            st.write(f"**Total Cost (Rp):** {total_cost:,.2f}")
            st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]}):** {freight_cost_mt:,.2f}")

            st.subheader("📈 Profit Scenario (0% - 50%)")
            st.dataframe(df_profit)

        # ===== PDF Generator =====
        def create_pdf_report():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("<b>Freight Report Calculator</b>", styles['Title']))
            elements.append(Spacer(1,12))

            # Voyage Info
            elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading3']))
            voyage_info = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Distance POL-POD (NM)", f"{distance_pol_pod}"],
                ["Distance POD-POL (NM)", f"{distance_pod_pol}"],
                ["Total Voyage (Days)", f"{total_voyage_days:,.2f}"]
            ]
            t_voyage = Table(voyage_info, hAlign='LEFT')
            t_voyage.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
            elements.append(t_voyage)
            elements.append(Spacer(1,12))

            # Calculations
            elements.append(Paragraph("<b>Calculations</b>", styles['Heading3']))
            calculation = [
                ["Sailing Time (Hour)", f"{sailing_time:,.2f}"],
                ["Fuel Consumption (liter)", f"{total_consumption_fuel:,.2f}"],
                ["Freshwater Consumption (Ton)", f"{total_consumption_fw:,.2f}"],
                ["Bunker Cost (Rp)", f"{bunker_cost:,.2f}"],
                ["Freshwater Cost (Rp)", f"{freshwater_cost:,.2f}"],
            ]
            if mode=="Owner":
                calculation += [
                    ["Installment (Rp)", f"{charter_cost:,.2f}"],
                    ["Crew Cost (Rp)", f"{crew_cost:,.2f}"],
                    ["Insurance Cost (Rp)", f"{insurance_cost:,.2f}"],
                    ["Docking Cost (Rp)", f"{docking_cost:,.2f}"],
                    ["Maintenance Cost (Rp)", f"{maintenance_cost:,.2f}"],
                    ["Certificate Cost (Rp)", f"{certificate_cost:,.2f}"],
                ]
            else:
                calculation += [["Charter Hire (Rp)", f"{charter_cost:,.2f}"]]

            calculation += [
                ["Premi Cost (Rp)", f"{premi_cost:,.2f}"],
                ["Port Costs (Rp)", f"{port_cost:,.2f}"],
                ["Other Cost (Rp)", f"{other_cost:,.2f}"]
            ]
            t_calc = Table(calculation, hAlign='LEFT')
            t_calc.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
            elements.append(t_calc)
            elements.append(Spacer(1,12))

            elements.append(Paragraph(f"<b>Total Cost (Rp):</b> {total_cost:,.2f}", styles['Heading3']))
            elements.append(Paragraph(f"<b>Freight Cost (Rp/{type_cargo.split()[1]}):</b> {freight_cost_mt:,.2f}", styles['Heading3']))
            elements.append(Spacer(1,12))

            # Profit Scenario
            elements.append(Paragraph("<b>Profit Scenario 0% - 50%</b>", styles['Heading3']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, hAlign='LEFT')
            t_profit.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.25, colors.black),
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
            ]))
            elements.append(t_profit)
            elements.append(Spacer(1,18))

            elements.append(Paragraph("<i>Generated By Freight Calculator APP Iqna</i>", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf_report()
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="Freight_Report_Calculator.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")
