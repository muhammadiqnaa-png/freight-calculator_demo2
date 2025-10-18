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
    st.markdown("<h2 style='text-align:center;'>🔐 Login Freight Calculator</h2>", unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["Masuk", "Daftar"])

    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Masuk 🚀"):
            ok, data = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Email atau password salah!")

    with tab_register:
        email = st.text_input("Email Daftar")
        password = st.text_input("Password Daftar", type="password")
        if st.button("Daftar 📝"):
            ok, data = register_user(email, password)
            if ok:
                st.success("Pendaftaran berhasil! Silakan login.")
            else:
                st.error("Gagal daftar. Email mungkin sudah terdaftar.")
    st.stop()

# ===== MAIN APP =====
# Tombol logout di sidebar atas
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Login as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Successfully logged out.")
    st.rerun()

# Mode
mode = st.sidebar.radio("Mode", ["Owner", "Charter"])

# === Gaya sidebar ===
st.markdown("""
    <style>
    section[data-testid="stSidebar"] .stNumberInput label {font-weight:500;}
    section[data-testid="stSidebar"] .stSubheader {color:#2b6cb0;font-weight:700;margin-top:15px;}
    </style>
""", unsafe_allow_html=True)

# ===== SIDEBAR PARAMETER =====
with st.sidebar.expander("🚢 Speed", expanded=True):
    speed_laden = st.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("🌊 Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel", expanded=True):
    consumption = st.number_input("Consumption Fuel (liter/h)", 0)
    price_fuel = st.number_input("Price Fuel (Rp/liter)", 0)

with st.sidebar.expander("💧 Freshwater", expanded=True):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/Day)", 0)
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0)

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost", expanded=True):
        charter = st.number_input("Angsuran (Rp/Month)", 0)
        crew = st.number_input("Crew (Rp/Month)", 0)
        insurance = st.number_input("Insurance (Rp/Month)", 0)
        docking = st.number_input("Docking (Rp/Month)", 0)
        maintenance = st.number_input("Maintenance (Rp/Month)", 0)
        certificate = st.number_input("Certificate (Rp/Month)", 0)
        premi_nm = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)
else:
    with st.sidebar.expander("🏗️ Charter Cost", expanded=True):
        charter = st.number_input("Charter Hire (Rp/Month)", 0)
        premi_nm = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

with st.sidebar.expander("⚓ Port Cost", expanded=True):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.number_input("Asist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay", expanded=True):
    port_stay_pol = st.number_input("POL (Days)", 0)
    port_stay_pod = st.number_input("POD (Days)", 0)

# ===== INPUT UTAMA =====
st.title("🚢 Freight Calculator Barge")

col1, col2 = st.columns(2)
with col1:
    port_pol = st.text_input("🏗️ Port of Loading (POL)")
with col2:
    port_pod = st.text_input("🏗️ Port of Discharge (POD)")

type_cargo = st.selectbox("📦 Type Cargo", ["Sand (M3)", "Split (M3)", "Coal (MT)", "Nickel (MT)"])
qyt_cargo = st.number_input("📊 Cargo Quantity", 0.0)
distance_pol_pod = st.number_input("📍 Distance POL - POD (NM)", 0.0)

# ===== PERHITUNGAN =====
if st.button("Calculate Freight Cost 💸"):
    try:
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pol_pod / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = round(consumption_fw * total_voyage_days)

        charter_cost = (charter / 30) * total_voyage_days if mode=="Owner" else (charter / 30) * total_voyage_days
        bunker_cost = total_consumption * price_fuel
        port_cost = port_cost_pol + port_cost_pod + asist_tug
        premi_cost = distance_pol_pod * premi_nm
        crew_cost = (crew /30)*total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance/30)*total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking/30)*total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance/30)*total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate/30)*total_voyage_days if mode=="Owner" else 0
        fw_cost = total_consumption_fw * price_fw

        total_cost = (
            charter_cost + bunker_cost + port_cost + premi_cost + crew_cost +
            insurance_cost + docking_cost + maintenance_cost + certificate_cost +
            other_cost + fw_cost
        )

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== TAMPILKAN HASIL UTAMA =====
        st.subheader("📋 Calculation Results")
        st.write(f"**Total Voyage (Days):** {total_voyage_days:.0f}")
        st.write(f"**Total Sailing Time (Hour):** {sailing_time:.0f}")
        st.write(f"**Total Consumption Fuel (liter):** {total_consumption:.0f}")
        st.write(f"**Total Consumption Freshwater (Ton):** {total_consumption_fw}")
        st.write(f"**Freshwater Cost (Rp):** Rp {fw_cost:,.0f}")
        st.write(f"**Total Cost (Rp):** Rp {total_cost:,.0f}")
        st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]}):** Rp {freight_cost_mt:,.0f}")

        # ===== TABEL PROFIT =====
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {profit:,.0f}"])

        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.dataframe(df_profit)

        # ===== PDF GENERATOR =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20,leftMargin=20, topMargin=20,bottomMargin=20)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            elements.append(Paragraph("<b>FREIGHT CALCULATOR REPORT</b>", styles['Title']))
            elements.append(Spacer(1,12))

            # Voyage Information
            elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading3']))
            voyage_info = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Cargo Quantity", f"{int(qyt_cargo):,} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod:.0f}"],
                ["Total Voyage (Days)", f"{total_voyage_days:.0f}"]
            ]
            t1 = Table(voyage_info, hAlign='LEFT', colWidths=[120,120])
            t1.setStyle(TableStyle([
                ("GRID",(0,0),(-1,-1),0.25,colors.black),
                ("ALIGN",(1,0),(-1,-1),"RIGHT")
            ]))
            elements.append(t1)
            elements.append(Spacer(1,12))

            # Calculation Results
            elements.append(Paragraph("<b>Calculation Results</b>", styles['Heading3']))
            calc_results = [
                ["Total Sailing Time (Hour)", f"{sailing_time:.0f}"],
                ["Total Consumption Fuel (liter)", f"Rp {total_consumption:,.0f}"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw}"],
                ["Freshwater Cost (Rp)", f"Rp {fw_cost:,.0f}"],
                ["Total Cost (Rp)", f"Rp {total_cost:,.0f}"],
                [f"Freight Cost (Rp/{type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"]
            ]
            t2 = Table(calc_results, hAlign='LEFT', colWidths=[180,120])
            t2.setStyle(TableStyle([
                ("GRID",(0,0),(-1,-1),0.25,colors.black),
                ("ALIGN",(1,0),(-1,-1),"RIGHT")
            ]))
            elements.append(t2)
            elements.append(Spacer(1,12))

            # Profit Scenario
            elements.append(Paragraph("<b>Profit Scenario 0-50%</b>", styles['Heading3']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t3 = Table(profit_table, hAlign='LEFT', colWidths=[60,100,100,100,100])
            t3.setStyle(TableStyle([
                ("GRID",(0,0),(-1,-1),0.25,colors.black),
                ("ALIGN",(1,0),(-1,-1),"RIGHT"),
                ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke)
            ]))
            elements.append(t3)
            elements.append(Spacer(1,12))

            elements.append(Paragraph(f"<i>Generated By: {st.secrets['APP_URL']}</i>", styles['Normal']))

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
