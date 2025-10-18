import streamlit as st
import math
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import requests

# ====== APP CONFIG ======
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
        email = st.text_input("Register Email")
        password = st.text_input("Register Password", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(email, password)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                st.error("Failed to register. Email may already be registered.")
    st.stop()

# ===== MAIN APP =====
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Successfully logged out.")
    st.rerun()

st.sidebar.title("⚙️ Calculation Parameters")

# === Sidebar Style ===
st.markdown("""
    <style>
    section[data-testid="stSidebar"] .stNumberInput label {font-weight:500;}
    section[data-testid="stSidebar"] .stSubheader {color:#2b6cb0;font-weight:700;margin-top:15px;}
    </style>
""", unsafe_allow_html=True)

# ====== SIDEBAR EXPANDERS ======
with st.sidebar.expander("🚢 Speed"):
    speed_laden = st.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("🌊 Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel"):
    consumption_fuel = st.number_input("Consumption Fuel (L/h)", 0)
    price_fuel = st.number_input("Price Fuel (Rp/L)", 0)

with st.sidebar.expander("💧 Freshwater"):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/Day)", 0)
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0)

mode = st.sidebar.radio("Mode Operation", ["Owner", "Charter"])

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        charter = st.number_input("Angsuran (Rp/Month)", 0)
        crew = st.number_input("Crew Cost (Rp/Month)", 0)
        insurance = st.number_input("Insurance (Rp/Month)", 0)
        docking = st.number_input("Docking - Saving (Rp/Month)", 0)
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
    asist_tug = st.number_input("Assist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay"):
    port_stay_pol = st.number_input("POL (Days)", 0)
    port_stay_pod = st.number_input("POD (Days)", 0)

# ===== INPUT MAIN =====
st.title("🚢 Freight Calculator Barge")

col1, col2, col3 = st.columns(3)
with col1:
    port_pol = st.text_input("Port of Loading (POL)")
with col2:
    port_pod = st.text_input("Port of Discharge (POD)")
with col3:
    type_cargo = st.selectbox("Type Cargo", ["Sand (M3)", "Split (M3)", "Coal (MT)", "Nickel (MT)"])

qyt_cargo = st.number_input("Cargo Quantity", 0.0)
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0)

# ====== CALCULATION ======
if st.button("Calculate Freight Cost 💸"):
    try:
        # Sailing time
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pol_pod / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_rounded = int(total_voyage_days) + (1 if total_voyage_days % 1 >= 0.5 else 0)

        # Consumption
        total_consumption_fuel = (sailing_time * consumption_fuel) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_rounded

        # Costs
        charter_cost = (charter / 30) * total_voyage_days if mode=="Owner" else (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode=="Owner" else 0
        bunker_cost = total_consumption_fuel * price_fuel
        freshwater_cost = total_consumption_fw * price_fw
        premi_cost = distance_pol_pod * premi
        port_cost = port_cost_pol + port_cost_pod + asist_tug

        total_cost = (
            charter_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost +
            certificate_cost + bunker_cost + freshwater_cost + premi_cost + port_cost + other_cost
        )
        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ====== MAIN RESULTS ======
        st.subheader("📋 Main Calculation Results")
        st.write(f"**Total Voyage (Days):** {int(total_voyage_days_rounded)}")
        st.write(f"**Total Sailing Time (Hour):** {int(sailing_time)}")
        st.write(f"**Total Consumption Fuel (L):** {int(total_consumption_fuel)}")
        st.write(f"**Total Consumption Freshwater (Ton):** {int(total_consumption_fw)}")
        st.write(f"**Fuel Cost (Rp):** {int(bunker_cost):,}")
        st.write(f"**Freshwater Cost (Rp):** {int(freshwater_cost):,}")
        if mode=="Owner":
            st.write(f"**Certificate Cost (Rp):** {int(certificate_cost):,}")
        st.write(f"**Total Cost (Rp):** {int(total_cost):,}")
        st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]}):** {int(freight_cost_mt):,}")

        # ====== PROFIT TABLE ======
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", int(freight_persen), int(revenue), int(pph), int(profit)])

        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.subheader("💹 Profit Scenario 0-50%")
        st.dataframe(df_profit, use_container_width=True)

        # ====== PDF GENERATOR ======
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("<b>Freight Report Calculator</b>", styles['Title']))
            elements.append(Spacer(1,12))

            # Voyage Info
            elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading2']))
            voyage_info = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod}"]
            ]
            t_info = Table(voyage_info, hAlign='LEFT')
            t_info.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
            elements.append(t_info)
            elements.append(Spacer(1,12))

            # Calculation Results
            elements.append(Paragraph("<b>Calculation Results</b>", styles['Heading2']))
            calc_results = [
                ["Total Voyage (Days)", int(total_voyage_days_rounded)],
                ["Total Sailing Time (Hour)", int(sailing_time)],
                ["Total Consumption Fuel (L)", int(total_consumption_fuel)],
                ["Total Consumption Freshwater (Ton)", int(total_consumption_fw)],
                ["Fuel Cost (Rp)", int(bunker_cost)],
                ["Freshwater Cost (Rp)", int(freshwater_cost)]
            ]
            if mode=="Owner":
                calc_results.append(["Certificate Cost (Rp)", int(certificate_cost)])
            calc_results.append(["Total Cost (Rp)", int(total_cost)])
            calc_results.append([f"Freight Cost (Rp/{type_cargo.split()[1]})", int(freight_cost_mt)])
            t_calc = Table(calc_results, hAlign='LEFT')
            t_calc.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
            elements.append(t_calc)
            elements.append(Spacer(1,12))

            # Profit Table
            elements.append(Paragraph("<b>Profit Scenario 0-50%</b>", styles['Heading2']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, hAlign='LEFT')
            t_profit.setStyle(TableStyle([
                ("GRID",(0,0),(-1,-1),0.25,colors.black),
                ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
            ]))
            elements.append(t_profit)
            elements.append(Spacer(1,18))

            elements.append(Paragraph(f"<i>Generated By: https://freight-calculatordemo2.streamlit.app/</i>", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="Freight_Report_Calculator.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")
