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
st.sidebar.markdown("### 👤 Akun")
st.sidebar.write(f"Login sebagai: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Berhasil logout.")
    st.rerun()

st.sidebar.markdown("### ⚙️ Parameter Perhitungan")
mode = st.sidebar.radio("Mode Operasi", ["Owner", "Charter"])

# === Vessel Performance ===
with st.sidebar.expander("🚢 Vessel Performance", expanded=True):
    speed_laden = st.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("🌊 Speed Ballast (knot)", 0.0)
    consumption = st.number_input("⛽ Consumption Fuel (liter/jam)", 0)
    price_fuel = st.number_input("💸 Price Fuel (Rp/liter)", 0)

# === Owner Mode ===
if mode == "Owner":
    with st.sidebar.expander("🏗️ Fixed Cost"):
        charter = st.number_input("📆 Charter (Rp/Month)", 0)
        crew = st.number_input("👨‍✈️ Crew cost (Rp/Month)", 0)
        insurance = st.number_input("🛡️ Insurance (Rp/Month)", 0)
        docking = st.number_input("⚓ Docking (Rp/Month)", 0)
        maintenance = st.number_input("🧰 Maintenance (Rp/Month)", 0)
        certificate = st.number_input("📜 Certificate (Rp/Month)", 0)

    with st.sidebar.expander("⚙️ Variable Cost"):
        premi_nm = st.number_input("📍 Premi (Rp/NM)", 0)
        port_cost_pol = st.number_input("🏗️ Port Cost POL (Rp)", 0)
        port_cost_pod = st.number_input("🏗️ Port Cost POD (Rp)", 0)
        asist_tug = st.number_input("🚤 Asist Tug (Rp)", 0)
        other_cost = st.number_input("💼 Other Cost (Rp)", 0)

# === Charter Mode ===
else:
    with st.sidebar.expander("📊 Voyage Cost"):
        charter = st.number_input("🚢 Charter hire/Month (Rp)", 0)
        premi_nm = st.number_input("📍 Premi (Rp/NM)", 0)
        port_cost_pol = st.number_input("🏗️ Port Cost POL (Rp)", 0)
        port_cost_pod = st.number_input("🏗️ Port Cost POD (Rp)", 0)
        asist_tug = st.number_input("🚤 Asist Tug (Rp)", 0)
        other_cost = st.number_input("💼 Other Cost (Rp)", 0)

# === Freshwater ===
with st.sidebar.expander("💧 Freshwater"):
    fw_consumption_day = st.number_input("📊 Consumption Freshwater (Ton/Day)", 0)
    fw_price = st.number_input("💧 Price Freshwater (Rp/Ton)", 0)

# === Port Stay ===
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

type_cargo = st.selectbox("📦 Type Cargo", ["Pasir (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"])
qyt_cargo = st.number_input("📊 QYT Cargo", 0.0)
distance_pol_pod = st.number_input("📍 Distance POL - POD (NM)", 0.0)
distance_pod_pol = st.number_input("📍 Distance POD - POL (NM)", 0.0)

# ===== PERHITUNGAN =====
if st.button("Hitung Freight Cost 💸"):
    try:
        # Total Sailing Time & Voyage
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        
        # Total Consumption
        total_consumption_fuel = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = round(total_voyage_days) * fw_consumption_day

        # Cost calculation
        charter_cost = (charter / 30) * total_voyage_days if mode=="Owner" else (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode=="Owner" else 0
        bunker_cost = total_consumption_fuel * price_fuel
        fw_cost = total_consumption_fw * fw_price
        port_cost = port_cost_pol + port_cost_pod
        premi_cost = distance_pol_pod * premi_nm

        total_cost = charter_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost + certificate_cost + bunker_cost + fw_cost + port_cost + premi_cost + asist_tug + other_cost
        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo>0 else 0

        # ===== Hasil Utama =====
        st.subheader("📋 Hasil Perhitungan Utama")
        with st.expander("Lihat Detail Perhitungan"):
            st.markdown(f"**Total Voyage (Days):** {total_voyage_days:,.2f}")
            st.markdown(f"**Total Sailing Time (Hour):** {sailing_time:,.2f}")
            st.markdown(f"**Total Consumption Fuel (L):** {total_consumption_fuel:,.2f}")
            st.markdown(f"**Total Consumption Freshwater (Ton):** {total_consumption_fw:,.2f}")
            st.markdown(f"**Charter Cost (Rp):** {charter_cost:,.2f}" if mode=="Owner" else f"Charter Hire Cost (Rp): {charter_cost:,.2f}")
            if mode=="Owner":
                st.markdown(f"Crew Cost (Rp): {crew_cost:,.2f}")
                st.markdown(f"Insurance Cost (Rp): {insurance_cost:,.2f}")
                st.markdown(f"Docking Cost (Rp): {docking_cost:,.2f}")
                st.markdown(f"Maintenance Cost (Rp): {maintenance_cost:,.2f}")
                st.markdown(f"Certificate Cost (Rp): {certificate_cost:,.2f}")
            st.markdown(f"Fuel Cost (Rp): {bunker_cost:,.2f}")
            st.markdown(f"Freshwater Cost (Rp): {fw_cost:,.2f}")
            st.markdown(f"Port Cost (Rp): {port_cost:,.2f}")
            st.markdown(f"Premi Cost (Rp): {premi_cost:,.2f}")
            st.markdown(f"Asist Tug (Rp): {asist_tug:,.2f}")
            st.markdown(f"Other Cost (Rp): {other_cost:,.2f}")
            st.markdown(f"**Total Cost (Rp):** {total_cost:,.2f}")
            st.markdown(f"**Freight Cost (Rp/{type_cargo.split()[1]}):** {freight_cost_mt:,.2f}")

        # ===== Tabel Profit =====
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p/100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"{freight_persen:,.2f}", f"{revenue:,.2f}", f"{pph:,.2f}", f"{profit:,.2f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.subheader("📊 Tabel Profit 0% - 50%")
        st.dataframe(df_profit)

        # ===== PDF GENERATOR =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("<b>Freight Calculator Barge</b>", styles['Title']))
            elements.append(Paragraph(f"<b>Mode:</b> {mode}", styles['Normal']))
            elements.append(Paragraph(f"<b>Port:</b> {port_pol} ➜ {port_pod}", styles['Normal']))
            elements.append(Spacer(1,12))

            elements.append(Paragraph("<b>Parameter Input</b>", styles['Heading3']))
            params = [
                ["Speed Laden", f"{speed_laden} knot"],
                ["Speed Ballast", f"{speed_ballast} knot"],
                ["Consumption Fuel", f"{consumption} L/h"],
                ["Price Fuel", f"Rp {price_fuel:,.0f}"],
                ["Consumption Freshwater", f"{fw_consumption_day} Ton/Day"],
                ["Price Freshwater", f"Rp {fw_price:,.0f}"],
                ["Distance POL-POD", f"{distance_pol_pod} NM"],
                ["Distance POD-POL", f"{distance_pod_pol} NM"],
                ["QYT Cargo", f"{qyt_cargo} {type_cargo.split()[1]}"]
            ]
            t = Table(params, hAlign='LEFT')
            t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(t)
            elements.append(Spacer(1,12))

            elements.append(Paragraph("<b>Hasil Perhitungan</b>", styles['Heading3']))
            hasil = [
                ["Total Voyage (Days)", f"{total_voyage_days:,.2f}"],
                ["Total Sailing Time (Hour)", f"{sailing_time:,.2f}"],
                ["Total Consumption Fuel (L)", f"{total_consumption_fuel:,.2f}"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.2f}"],
                ["Charter Cost (Rp)", f"{charter_cost:,.2f}"] if mode=="Owner" else ["Charter Hire Cost (Rp)", f"{charter_cost:,.2f}"],
            ]
            if mode=="Owner":
                hasil += [
                    ["Crew Cost (Rp)", f"{crew_cost:,.2f}"],
                    ["Insurance Cost (Rp)", f"{insurance_cost:,.2f}"],
                    ["Docking Cost (Rp)", f"{docking_cost:,.2f}"],
                    ["Maintenance Cost (Rp)", f"{maintenance_cost:,.2f}"],
                    ["Certificate Cost (Rp)", f"{certificate_cost:,.2f}"],
                ]
            hasil += [
                ["Fuel Cost (Rp)", f"{bunker_cost:,.2f}"],
                ["Freshwater Cost (Rp)", f"{fw_cost:,.2f}"],
                ["Port Cost (Rp)", f"{port_cost:,.2f}"],
                ["Premi Cost (Rp)", f"{premi_cost:,.2f}"],
                ["Asist Tug (Rp)", f"{asist_tug:,.2f}"],
                ["Other Cost (Rp)", f"{other_cost:,.2f}"],
                ["Total Cost (Rp)", f"{total_cost:,.2f}"],
                ["Freight Cost", f"{freight_cost_mt:,.2f}"]
            ]
            t2 = Table(hasil, hAlign='LEFT')
            t2.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(t2)
            elements.append(Spacer(1,12))

            elements.append(Paragraph("<b>Tabel Profit 0% - 50%</b>", styles['Heading3']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t3 = Table(profit_table, hAlign='LEFT')
            t3.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black),("BACKGROUND",(0,0),(-1,0),colors.lightgrey)]))
            elements.append(t3)
            elements.append(Spacer(1,18))
            elements.append(Paragraph("<i>Generated By Freight Calculator APP Iqna</i>", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()
        st.download_button("📥 Download PDF Hasil", data=pdf_buffer, file_name="Freight_Calculator_Barge.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
