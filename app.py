import streamlit as st
import math
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import requests

st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# ====== FIREBASE AUTH ======
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
    st.markdown("<h2 style='text-align:center;'>🔐 Login Freight Calculator</h2>", unsafe_allow_html=True)
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
                st.error("Email or password incorrect!")

    with tab_register:
        email = st.text_input("Email for Registration")
        password = st.text_input("Password for Registration", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(email, password)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                st.error("Registration failed. Email may already exist.")
    st.stop()

# ===== MAIN APP =====
# Logout button
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Logged out successfully.")
    st.rerun()

# Mode selection
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# ===== Sidebar Parameters with Expander Groups =====
with st.sidebar.expander("🚢 Speed", expanded=True):
    speed_laden = st.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("🌊 Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel", expanded=True):
    consumption_fuel = st.number_input("Consumption Fuel (liter/hour)", 0)
    price_fuel = st.number_input("Price Fuel (Rp/liter)", 0)

with st.sidebar.expander("💧 Freshwater", expanded=True):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/Day)", 0)
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0)

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost", expanded=True):
        charter = st.number_input("Installment (Rp/Month)", 0)
        crew = st.number_input("Crew (Rp/Month)", 0)
        insurance = st.number_input("Insurance (Rp/Month)", 0)
        docking = st.number_input("Docking (Rp/Month)", 0)
        maintenance = st.number_input("Maintenance (Rp/Month)", 0)
        certificate = st.number_input("Certificate (Rp/Month)", 0)
        premi = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)
else:
    with st.sidebar.expander("🏗️ Charter Cost", expanded=True):
        charter = st.number_input("Charter Hire (Rp/Month)", 0)
        premi = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

with st.sidebar.expander("⚓ Port Cost", expanded=True):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.number_input("Assist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay (Days)", expanded=True):
    port_stay_pol = st.number_input("POL (Days)", 0)
    port_stay_pod = st.number_input("POD (Days)", 0)

# ===== Main Page Inputs =====
st.title("🚢 Freight Calculator Barge")

col1, col2 = st.columns(2)
with col1:
    port_pol = st.text_input("Port of Loading")
with col2:
    port_pod = st.text_input("Port of Discharge")

type_cargo = st.selectbox("Type Cargo", ["Sand (M3)", "Split (M3)", "Coal (MT)", "Nickel (MT)"])
qyt_cargo = st.number_input("Cargo Quantity", 0.0, step=1.0)
distance_pol_pod = st.number_input("Distance POL-POD (NM)", 0.0, step=1.0)

# ===== Calculation =====
if st.button("Calculate Freight 💸"):
    try:
        sailing_time = (distance_pol_pod / speed_laden if speed_laden>0 else 0) + \
                       (distance_pol_pod / speed_ballast if speed_ballast>0 else 0)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_consumption_fuel = (sailing_time * consumption_fuel) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * round(total_voyage_days)
        freshwater_cost = total_consumption_fw * price_fw

        certificate_cost = (certificate / 30) * total_voyage_days if mode=="Owner" else 0
        charter_cost = (charter / 30) * total_voyage_days
        bunker_cost = total_consumption_fuel * price_fuel
        port_cost = port_cost_pol + port_cost_pod + asist_tug
        premi_cost = distance_pol_pod * premi
        crew_cost = (crew / 30) * total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance /30) * total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking /30) * total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance /30) * total_voyage_days if mode=="Owner" else 0

        total_cost = charter_cost + bunker_cost + port_cost + premi_cost + crew_cost + \
                     insurance_cost + docking_cost + maintenance_cost + certificate_cost + other_cost + freshwater_cost
        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo>0 else 0

        # ===== Display Calculation Results =====
        st.subheader("📋 Calculation Results")
        st.write(f"**Total Voyage (days)**: {int(total_voyage_days)}")
        st.write(f"**Total Sailing Time (hours)**: {int(sailing_time)}")
        st.write(f"**Total Fuel Consumption (liter)**: {int(total_consumption_fuel)}")
        st.write(f"**Total Freshwater Consumption (Ton)**: {int(total_consumption_fw)}")
        st.write(f"**Freshwater Cost (Rp)**: Rp {int(freshwater_cost):,}")
        if mode=="Owner":
            st.write(f"**Certificate (Rp)**: Rp {int(certificate_cost):,}")
        st.write(f"**Port Cost (Rp)**: Rp {int(port_cost):,}")
        st.write(f"**Premi Cost (Rp)**: Rp {int(premi_cost):,}")
        if mode=="Owner":
            st.write(f"**Crew Cost (Rp)**: Rp {int(crew_cost):,}")
            st.write(f"**Insurance Cost (Rp)**: Rp {int(insurance_cost):,}")
            st.write(f"**Docking Cost (Rp)**: Rp {int(docking_cost):,}")
            st.write(f"**Maintenance Cost (Rp)**: Rp {int(maintenance_cost):,}")
        st.write(f"**Charter/Installment Cost (Rp)**: Rp {int(charter_cost):,}")
        st.write(f"**Other Cost (Rp)**: Rp {int(other_cost):,}")
        st.write(f"**💰 Total Cost (Rp)**: Rp {int(total_cost):,}")
        st.write(f"**💵 Freight Cost ({type_cargo.split()[1]})**: Rp {int(freight_cost_mt):,}")

        # ===== Profit Scenario =====
        st.subheader("💹 Profit Scenario 0%-50%")
        profit_data = []
        for p in range(0, 55,5):
            freight_scenario = freight_cost_mt*(1+p/100)
            revenue = freight_scenario * qyt_cargo
            pph = revenue*0.012
            profit = revenue - total_cost - pph
            profit_data.append([f"{p}%", f"Rp {int(freight_scenario):,}", f"Rp {int(revenue):,}", f"Rp {int(pph):,}", f"Rp {int(profit):,}"])
        df_profit = pd.DataFrame(profit_data, columns=["Profit %","Freight (Rp)","Revenue (Rp)","PPH 1.2% (Rp)","Profit (Rp)"])
        st.dataframe(df_profit)

        # ===== PDF Generator =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            styleN = styles['Normal']
            styleB = ParagraphStyle('Bold', parent=styleN, fontName='Helvetica-Bold')
            elements = []

            elements.append(Paragraph("<b>Freight Calculator Report</b>", styles['Title']))
            elements.append(Spacer(1,12))

            # Voyage Information
            elements.append(Paragraph("<b>Voyage Information</b>", styleB))
            voyage_data = [
                ["Port of Loading", port_pol],
                ["Port of Discharge", port_pod],
                ["Cargo Quantity", f"{int(qyt_cargo):,} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{int(distance_pol_pod):,}"],
                ["Total Voyage (days)", f"{int(total_voyage_days):,}"]
            ]
            t_voyage = Table(voyage_data, hAlign='LEFT')
            t_voyage.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
            elements.append(t_voyage)
            elements.append(Spacer(1,12))

            # Calculation Results
            elements.append(Paragraph("<b>Calculation Results</b>", styleB))
            calc_data = [
                ["Total Sailing Time (hours)", f"{int(sailing_time):,}"],
                ["Total Fuel Consumption (liter)", f"{int(total_consumption_fuel):,}"],
                ["Total Freshwater Consumption (Ton)", f"{int(total_consumption_fw):,}"],
                ["Freshwater Cost (Rp)", f"Rp {int(freshwater_cost):,}"]
            ]
            if mode=="Owner":
                calc_data += [["Certificate (Rp)", f"Rp {int(certificate_cost):,}"]]
            calc_data += [["Port Cost (Rp)", f"Rp {int(port_cost):,}"],
                          ["Premi Cost (Rp)", f"Rp {int(premi_cost):,}"],
                          ["Charter/Installment Cost (Rp)", f"Rp {int(charter_cost):,}"]]
            if mode=="Owner":
                calc_data += [["Crew Cost (Rp)", f"Rp {int(crew_cost):,}"],
                              ["Insurance Cost (Rp)", f"Rp {int(insurance_cost):,}"],
                              ["Docking Cost (Rp)", f"Rp {int(docking_cost):,}"],
                              ["Maintenance Cost (Rp)", f"Rp {int(maintenance_cost):,}"]]
            calc_data += [["Other Cost (Rp)", f"Rp {int(other_cost):,}"],
                          ["💰 Total Cost (Rp)", f"Rp {int(total_cost):,}"],
                          ["💵 Freight Cost (Rp)", f"Rp {int(freight_cost_mt):,}"]]

            t_calc = Table(calc_data, hAlign='LEFT', colWidths=[200,200])
            t_calc.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black),
                                        ("ALIGN",(1,0),(-1,-1),"RIGHT"),
                                        ("ALIGN",(0,0),(0,-1),"LEFT")]))
            elements.append(t_calc)
            elements.append(Spacer(1,12))

            # Profit Scenario
            elements.append(Paragraph("<b>Profit Scenario 0%-50%</b>", styleB))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, hAlign='LEFT', colWidths=[60,100,100,100,100])
            t_profit.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black),
                                          ("ALIGN",(1,1),(-1,-1),"RIGHT"),
                                          ("ALIGN",(0,0),(0,-1),"LEFT"),
                                          ("BACKGROUND",(0,0),(-1,0),colors.white)]))
            elements.append(t_profit)
            elements.append(Spacer(1,12))

            # Footer
            elements.append(Paragraph("Generated By: https://freight-calculatordemo2.streamlit.app/", styleN))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="Freight_Calculator_Report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")
