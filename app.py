import streamlit as st
import math
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import requests
import base64
import streamlit.components.v1 as components

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
# Logout
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Logged out successfully.")
    st.rerun()

# Mode
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# === Parameter Groups ===
with st.sidebar.expander("🚢 Speed"):
    speed_laden = st.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("🌊 Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel"):
    consumption = st.number_input("⛽ Consumption Fuel (liter/h)", 0)
    price_fuel = st.number_input("💸 Price Fuel (Rp/Ltr)", 0)

with st.sidebar.expander("💧 Freshwater"):
    consumption_fw = st.number_input("💧 Consumption Freshwater (Ton/Day)", 0)
    price_fw = st.number_input("💧 Price Freshwater (Rp/Ton)", 0)

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        charter = st.number_input("📆 Angsuran (Rp/Month)", 0)
        crew = st.number_input("👨‍✈️ Crew cost (Rp/Month)", 0)
        insurance = st.number_input("🛡️ Insurance (Rp/Month)", 0)
        docking = st.number_input("⚓ Docking (Rp/Month)", 0)
        maintenance = st.number_input("🧰 Maintenance (Rp/Month)", 0)
        certificate = st.number_input("📜 Certificate (Rp/Month)", 0)
        premi = st.number_input("📍 Premi (Rp/NM)", 0)
        other_cost = st.number_input("💼 Other Cost (Rp)", 0)
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        charter = st.number_input("🚢 Charter Hire (Rp/Month)", 0)
        premi = st.number_input("📍 Premi (Rp/NM)", 0)
        other_cost = st.number_input("💼 Other Cost (Rp)", 0)

with st.sidebar.expander("⚓ Port Cost"):
    port_cost_pol = st.number_input("🏗️ Port Cost POL (Rp)", 0)
    port_cost_pod = st.number_input("🏗️ Port Cost POD (Rp)", 0)
    asist_tug = st.number_input("🚤 Asist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay (Days)"):
    port_stay_pol = st.number_input("🅿️ POL (Hari)", 0)
    port_stay_pod = st.number_input("🅿️ POD (Hari)", 0)

# ===== INPUT UTAMA =====
st.title("🚢 Freight Calculator Barge")

col1, col2 = st.columns(2)
with col1:
    port_pol = st.text_input("🏗️ Port of Loading (POL)")
with col2:
    port_pod = st.text_input("🏗️ Port of Discharge (POD)")

type_cargo = st.selectbox("📦 Type Cargo", ["Bauxite (M3)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"])
qyt_cargo = st.number_input("📊 Cargo Quantity", 0.0, format="%.0f")
distance_pol_pod = st.number_input("📍 Distance POL - POD (NM)", 0.0, format="%.0f")
distance_pod_pol = st.number_input("📍 Distance POD - POL (NM)", 0.0, format="%.0f")

# ===== PERHITUNGAN =====
if st.button("Calculate Freight 💸"):
    try:
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_round = math.floor(total_voyage_days) if total_voyage_days - math.floor(total_voyage_days) < 0.5 else math.ceil(total_voyage_days)

        total_consumption_fuel = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_round
        cost_fw = total_consumption_fw * price_fw

        charter_cost = (charter / 30) * total_voyage_days if mode=="Owner" else (charter / 30) * total_voyage_days
        fuel_cost = total_consumption_fuel * price_fuel
        port_cost = port_cost_pol + port_cost_pod + asist_tug
        premi_cost = distance_pol_pod * premi
        crew_cost = (crew / 30) * total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode=="Owner" else 0

        total_cost = charter_cost + fuel_cost + port_cost + premi_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost + certificate_cost + other_cost + cost_fw
        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== TAMPILKAN HASIL =====
        st.subheader("📋 Calculation Results")
        st.write(f"**Total Voyage (Days):** {total_voyage_days_round}")
        st.write(f"**Total Sailing Time (Hours):** {int(sailing_time)}")
        st.write(f"**Total Consumption Fuel (L):** {int(total_consumption_fuel)}")
        st.write(f"**Total Consumption Freshwater (Ton):** {int(total_consumption_fw)}")
        st.write(f"**Freshwater Cost (Rp):** {int(cost_fw):,}")
        st.write(f"**Fuel Cost (Rp):** {int(fuel_cost):,}")
        st.write(f"**Port Cost (Rp):** {int(port_cost):,}")
        if mode=="Owner":
            st.write(f"**Owner Cost (Rp):** {int(charter_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost + certificate_cost + premi_cost + other_cost):,}")
        else:
            st.write(f"**Charter Cost (Rp):** {int(charter_cost + premi_cost + other_cost):,}")
        st.write(f"**Total Cost (Rp):** {int(total_cost):,}")
        st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]}):** {int(freight_cost_mt):,}")

        # ===== TABEL PROFIT =====
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"{int(freight_persen):,}", f"{int(revenue):,}", f"{int(pph):,}", f"{int(profit):,}"])
        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.subheader("📊 Profit Scenario 0-50%")
        st.dataframe(df_profit)

        # ===== PDF GENERATOR =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            elements.append(Paragraph("<b>Freight Calculator Report</b>", styles['Title']))
            elements.append(Spacer(1,12))

            # Voyage Info
            elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading2']))
            voyage_data = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Cargo Quantity", f"{int(qyt_cargo):,} {type_cargo.split()[1]}"],
                ["Distance (NM)", int(distance_pol_pod)],
                ["Total Voyage (Days)", total_voyage_days_round]
            ]
            t1 = Table(voyage_data, hAlign='LEFT', colWidths=[150,200])
            t1.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(t1)
            elements.append(Spacer(1,12))

            # Calculation Results
            elements.append(Paragraph("<b>Calculation Results</b>", styles['Heading2']))
            calc_data = [
                ["Total Sailing Time (Hours)", int(sailing_time)],
                ["Total Consumption Fuel (L)", int(total_consumption_fuel)],
                ["Fuel Cost (Rp)", int(fuel_cost)],
                ["Total Consumption Freshwater (Ton)", int(total_consumption_fw)],
                ["Freshwater Cost (Rp)", int(cost_fw)],
                ["Port Cost (Rp)", int(port_cost)],
            ]
            if mode=="Owner":
                calc_data.append(["Owner Cost (Rp)", int(charter_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost + certificate_cost + premi_cost + other_cost)])
            else:
                calc_data.append(["Charter Cost (Rp)", int(charter_cost + premi_cost + other_cost)])
            calc_data.append(["Total Cost (Rp)", int(total_cost)])
            calc_data.append([f"Freight Cost (Rp/{type_cargo.split()[1]})", int(freight_cost_mt)])
            t2 = Table(calc_data, hAlign='LEFT', colWidths=[200,200])
            t2.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(t2)
            elements.append(Spacer(1,12))

            # Profit Table
            elements.append(Paragraph("<b>Profit Scenario 0-50%</b>", styles['Heading2']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t3 = Table(profit_table, hAlign='LEFT', colWidths=[60,80,80,80,80])
            t3.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(t3)
            elements.append(Spacer(1,12))

            # Footer
            elements.append(Paragraph("<i>Generated By: https://freight-calculatordemo2.streamlit.app/</i>", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()

        # ===== PDF Download & Preview =====
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="Freight_Calculator_Report.pdf",
            mime="application/pdf"
        )

        # PDF Preview
        def show_pdf(buffer):
            base64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
            components.html(pdf_display, height=900)
        pdf_buffer.seek(0)
        show_pdf(pdf_buffer)

    except Exception as e:
        st.error(f"An error occurred: {e}")
