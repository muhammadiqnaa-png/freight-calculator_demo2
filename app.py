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
                st.error("Incorrect email or password!")

    with tab_register:
        email = st.text_input("Register Email")
        password = st.text_input("Register Password", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(email, password)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                st.error("Failed to register. Email may already exist.")
    st.stop()

# ===== MAIN APP =====
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Successfully logged out.")
    st.rerun()

# ===== Sidebar Mode =====
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# ===== Sidebar Parameters with Expanders =====
with st.sidebar.expander("🚢 Speed"):
    speed_laden = st.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel"):
    consumption = st.number_input("Consumption Fuel (Ltr/hour)", 0.0)
    price_fuel = st.number_input("Price Fuel (Rp/Ltr)", 0.0)

with st.sidebar.expander("💧 Freshwater"):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/Day)", 0.0)
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0.0)

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        charter = st.number_input("Angsuran (Rp/Month)", 0)
        crew = st.number_input("Crew Cost (Rp/Month)", 0)
        insurance = st.number_input("Insurance (Rp/Month)", 0)
        docking = st.number_input("Docking (Rp/Month)", 0)
        maintenance = st.number_input("Maintenance (Rp/Month)", 0)
        certificate = st.number_input("Certificate (Rp/Month)", 0)
        premi_nm = st.number_input("Premium (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        charter = st.number_input("Charter Hire (Rp/Month)", 0)
        premi_nm = st.number_input("Premium (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

with st.sidebar.expander("⚓ Port Cost"):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.number_input("Asist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay (Days)"):
    port_stay_pol = st.number_input("POL (Days)", 0)
    port_stay_pod = st.number_input("POD (Days)", 0)

# ===== Main Inputs =====
st.title("🚢 Freight Calculator Barge")

col1, col2 = st.columns(2)
with col1:
    port_pol = st.text_input("Port of Loading")
with col2:
    port_pod = st.text_input("Port of Discharge")

next_port = st.text_input("Next Port")
type_cargo = st.selectbox("Type Cargo", ["Bauxite (M3)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"])
qyt_cargo = st.number_input("Cargo Quantity", 0.0)
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0)
distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0)

# ===== Calculation =====
if st.button("Calculate Freight 💸"):
    try:
        # Sailing & Voyage
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)

        # Consumption
        total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days

        # Cost
        charter_cost = (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode=="Owner" else 0
        bunker_cost = total_consumption * price_fuel
        freshwater_cost = total_consumption_fw * price_fw
        premi_cost = distance_pol_pod * premi_nm

        port_cost = port_cost_pol + port_cost_pod + asist_tug

        total_cost = (
            charter_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost + certificate_cost +
            bunker_cost + freshwater_cost + premi_cost + port_cost + other_cost
        )

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== Profit Table =====
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"{freight_persen:,.0f}", f"{revenue:,.0f}", f"{pph:,.0f}", f"{profit:,.0f}"])

        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])

        # ===== Display Results =====
        st.subheader("📋 Calculation Results")
        st.write(f"**Total Voyage (Days):** {total_voyage_days:,.0f}")
        st.write(f"**Sailing Time (Hour):** {sailing_time:,.0f}")
        st.write(f"**Total Consumption Fuel (Ltr):** {total_consumption:,.0f}")
        st.write(f"**Total Consumption Freshwater (Ton):** {total_consumption_fw:,.0f}")
        st.write(f"**Freshwater Cost (Rp):** {freshwater_cost:,.0f}")
        st.write(f"**Total Cost (Rp):** {total_cost:,.0f}")
        st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]}):** {freight_cost_mt:,.0f}")
        st.dataframe(df_profit)

        # ===== PDF Generator =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            elements.append(Paragraph("<b><font size=14>Freight Calculator Report</font></b>", styles['Title']))
            elements.append(Spacer(1, 12))

            # Voyage Information
            elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading3']))
            voyage_info = [
                ["Port of Loading", port_pol],
                ["Port of Discharge", port_pod],
                ["Next Port", next_port],
                ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod:,.0f}"]
            ]
            t1 = Table(voyage_info, hAlign='LEFT', colWidths=[150, 200])
            t1.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black),
                                    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                    ("ALIGN", (1,0), (-1,-1), "RIGHT")]))
            elements.append(t1)
            elements.append(Spacer(1, 12))

            # Calculation Results
            elements.append(Paragraph("<b>Calculation Results</b>", styles['Heading3']))
            calc_results = [
                ["Total Voyage (Days)", f"{total_voyage_days:,.0f}"],
                ["Sailing Time (Hour)", f"{sailing_time:,.0f}"],
                ["Total Consumption Fuel (Ltr)", f"{total_consumption:,.0f}"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.0f}"],
                ["Freshwater Cost (Rp)", f"{freshwater_cost:,.0f}"],
                ["Charter Cost (Rp)", f"{charter_cost:,.0f}"] if mode=="Charter" else None,
                ["Angsuran (Rp)", f"{charter_cost:,.0f}"] if mode=="Owner" else None,
                ["Crew Cost (Rp)", f"{crew_cost:,.0f}"] if mode=="Owner" else None,
                ["Insurance Cost (Rp)", f"{insurance_cost:,.0f}"] if mode=="Owner" else None,
                ["Docking Cost (Rp)", f"{docking_cost:,.0f}"] if mode=="Owner" else None,
                ["Maintenance Cost (Rp)", f"{maintenance_cost:,.0f}"] if mode=="Owner" else None,
                ["Certificate (Rp)", f"{certificate_cost:,.0f}"] if mode=="Owner" else None,
                ["Premium Cost (Rp)", f"{premi_cost:,.0f}"],
                ["Port Cost POL (Rp)", f"{port_cost_pol:,.0f}"],
                ["Port Cost POD (Rp)", f"{port_cost_pod:,.0f}"],
                ["Asist Tug (Rp)", f"{asist_tug:,.0f}"],
                ["Other Cost (Rp)", f"{other_cost:,.0f}"],
                ["Total Cost (Rp)", f"<b>{total_cost:,.0f}</b>"],
                [f"Freight Cost (Rp/{type_cargo.split()[1]})", f"<b>{freight_cost_mt:,.0f}</b>"]
            ]
            calc_results = [row for row in calc_results if row]
            t2 = Table(calc_results, hAlign='LEFT', colWidths=[200, 150])
            t2.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black),
                                    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                    ("ALIGN", (1,0), (-1,-1), "RIGHT")]))
            elements.append(t2)
            elements.append(Spacer(1, 12))

            # Profit Scenario
            elements.append(Paragraph("<b>Profit Scenario 0-50%</b>", styles['Heading3']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t3 = Table(profit_table, hAlign='LEFT', colWidths=[80, 100, 100, 100, 100])
            t3.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.25, colors.black),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ALIGN", (1,1), (-1,-1), "RIGHT"),
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
            ]))
            elements.append(t3)
            elements.append(Spacer(1, 18))

            # Footer
            elements.append(Paragraph("<i>Generated By: https://freight-calculatordemo2.streamlit.app/</i>", styles['Normal']))

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
        st.error(f"An error occurred: {e}")
