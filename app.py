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

st.sidebar.title("⚙️ Parameter Perhitungan")
mode = st.sidebar.radio("Mode Operasi", ["Owner", "Charter"])

# === SIDEBAR COMPACT ===
def number_inputs_inline(labels, defaults):
    cols = st.sidebar.columns(len(labels))
    values = []
    for i, label in enumerate(labels):
        values.append(cols[i].number_input(label, value=defaults[i]))
    return values

# ===== PARAMETERS =====
# Vessel Performance
st.sidebar.subheader("🚢 Vessel Performance")
speed_laden, speed_ballast, consumption, price_fuel, consumption_fw, price_fw = number_inputs_inline(
    ["⚓ Speed Laden", "🌊 Speed Ballast", "⛽ Consumption Fuel", "💸 Price Fuel", "💧 Consumption Freshwater", "💦 Price Freshwater"],
    [0.0,0.0,0,0,0.0,0]
)

# Fixed / Voyage Cost
if mode=="Owner":
    st.sidebar.subheader("🏗️ Fixed Cost (Rp/Month)")
    charter, crew, insurance, docking, maintenance, certificate = number_inputs_inline(
        ["📆 Charter","👨‍✈️ Crew","🛡️ Insurance","⚓ Docking","🧰 Maintenance","📜 Certificate"],
        [0,0,0,0,0,0]
    )
else:
    st.sidebar.subheader("📊 Voyage Cost")
    charter, premi_nm, port_cost_pol, port_cost_pod, asist_tug, other_cost = number_inputs_inline(
        ["🚢 Charter","📍 Premi","🏗️ POL","🏗️ POD","🚤 Asist Tug","💼 Other Cost"],
        [0,0,0,0,0,0]
    )

# Port Stay
st.sidebar.subheader("🕓 Port Stay (Days)")
port_stay_pol, port_stay_pod = number_inputs_inline(["🅿️ POL","🅿️ POD"], [0,0])

# ===== INPUT UTAMA =====
st.title("🚢 Freight Calculator Barge")
col1, col2 = st.columns(2)
with col1:
    port_pol = st.text_input("🏗️ Port of Loading (POL)")
with col2:
    port_pod = st.text_input("🏗️ Port of Discharge (POD)")

type_cargo = st.selectbox("📦 Type Cargo", ["Pasir (M3)","Split (MT)","Coal (MT)","Nickel (MT)"])
qyt_cargo = st.number_input("📊 QYT Cargo", 0.0)
distance_pol_pod = st.number_input("📍 Distance POL-POD (NM)",0.0)
distance_pod_pol = st.number_input("📍 Distance POD-POL (NM)",0.0)

# ===== PERHITUNGAN =====
if st.button("Hitung Freight Cost 💸"):
    try:
        # Sailing & Voyage
        sailing_time = (distance_pol_pod/speed_laden)+(distance_pod_pol/speed_ballast)
        total_voyage_days = (sailing_time/24)+(port_stay_pol+port_stay_pod)
        total_consumption = (sailing_time*consumption)+((port_stay_pol+port_stay_pod)*120)
        total_consumption_fw = round(total_voyage_days)*consumption_fw

        # Costs
        charter_cost = (charter/30)*total_voyage_days if mode=="Owner" else 0
        crew_cost = (crew/30)*total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance/30)*total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking/30)*total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance/30)*total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate/30)*total_voyage_days if mode=="Owner" else 0

        bunker_cost = total_consumption*price_fuel
        freshwater_cost = total_consumption_fw*price_fw

        if mode=="Owner":
            total_cost = charter_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost + certificate_cost + bunker_cost + freshwater_cost
        else:
            total_cost = charter + premi_nm*distance_pol_pod + port_cost_pol + port_cost_pod + asist_tug + other_cost + bunker_cost + freshwater_cost

        freight_cost_mt = total_cost/qyt_cargo if qyt_cargo>0 else 0

        # ===== TAMPILKAN HASIL UTAMA =====
        st.subheader("📋 Hasil Perhitungan Utama")
        st.write(f"**Total Voyage Days:** {total_voyage_days:,.2f} hari")
        st.write(f"**Total Sailing Time:** {sailing_time:,.2f} jam")
        st.write(f"**Total Fuel Consumption:** {total_consumption:,.2f} liter")
        st.write(f"**Total Freshwater Consumption:** {total_consumption_fw:,.2f} Ton")
        st.write(f"**Fuel Cost:** Rp {bunker_cost:,.2f}")
        st.write(f"**Freshwater Cost:** Rp {freshwater_cost:,.2f}")
        if mode=="Owner":
            st.write(f"**Charter Cost:** Rp {charter_cost:,.2f}")
            st.write(f"**Crew Cost:** Rp {crew_cost:,.2f}")
            st.write(f"**Insurance Cost:** Rp {insurance_cost:,.2f}")
            st.write(f"**Docking Cost:** Rp {docking_cost:,.2f}")
            st.write(f"**Maintenance Cost:** Rp {maintenance_cost:,.2f}")
            st.write(f"**Certificate Cost:** Rp {certificate_cost:,.2f}")
        st.write(f"**Total Cost:** Rp {total_cost:,.2f}")
        st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]}):** {freight_cost_mt:,.2f}")

        # ===== TABEL PROFIT =====
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p/100)
            revenue = freight_persen*qyt_cargo
            pph = revenue*0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"{freight_persen:,.2f}", f"{revenue:,.2f}", f"{pph:,.2f}", f"{profit:,.2f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %","Freight (Rp)","Revenue (Rp)","PPH 1.2% (Rp)","Profit (Rp)"])
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

            # Parameter
            elements.append(Paragraph("<b>Parameter Input</b>", styles['Heading3']))
            params = [
                ["Speed Laden", f"{speed_laden} knot"],
                ["Speed Ballast", f"{speed_ballast} knot"],
                ["Consumption Fuel", f"{consumption} L/h"],
                ["Price Fuel", f"Rp {price_fuel:,.0f}"],
                ["Consumption Freshwater", f"{consumption_fw} Ton/day"],
                ["Price Freshwater", f"Rp {price_fw:,.0f}"]
            ]
            if mode=="Owner":
                params += [
                    ["Charter", f"Rp {charter:,.0f}"],
                    ["Crew", f"Rp {crew:,.0f}"],
                    ["Insurance", f"Rp {insurance:,.0f}"],
                    ["Docking", f"Rp {docking:,.0f}"],
                    ["Maintenance", f"Rp {maintenance:,.0f}"],
                    ["Certificate", f"Rp {certificate:,.0f}"]
                ]
            else:
                params += [
                    ["Charter", f"Rp {charter:,.0f}"],
                    ["Premi", f"Rp {premi_nm:,.0f}/NM"],
                    ["Port Cost POL", f"Rp {port_cost_pol:,.0f}"],
                    ["Port Cost POD", f"Rp {port_cost_pod:,.0f}"],
                    ["Asist Tug", f"Rp {asist_tug:,.0f}"],
                    ["Other Cost", f"Rp {other_cost:,.0f}"]
                ]
            t = Table(params, hAlign='LEFT')
            t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(t)
            elements.append(Spacer(1,12))

            # Hasil Perhitungan
            elements.append(Paragraph("<b>Hasil Perhitungan</b>", styles['Heading3']))
            hasil = [
                ["Total Voyage Days", f"{total_voyage_days:,.2f}"],
                ["Total Sailing Time (h)", f"{sailing_time:,.2f}"],
                ["Total Fuel Consumption (L)", f"{total_consumption:,.2f}"],
                ["Total Freshwater Consumption (Ton)", f"{total_consumption_fw:,.2f}"],
                ["Fuel Cost (Rp)", f"{bunker_cost:,.2f}"],
                ["Freshwater Cost (Rp)", f"{freshwater_cost:,.2f}"],
                ["Total Cost (Rp)", f"{total_cost:,.2f}"],
                ["Freight Cost (Rp/"+type_cargo.split()[1]+")", f"{freight_cost_mt:,.2f}"]
            ]
            t2 = Table(hasil, hAlign='LEFT')
            t2.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(t2)
            elements.append(Spacer(1,12))

            # Profit Table
            elements.append(Paragraph("<b>Tabel Profit 0% - 50%</b>", styles['Heading3']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t3 = Table(profit_table, hAlign='LEFT')
            t3.setStyle(TableStyle([
                ("GRID",(0,0),(-1,-1),0.25,colors.black),
                ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
            ]))
            elements.append(t3)
            elements.append(Spacer(1,18))

            elements.append(Paragraph("<i>Generated By Freight Calculator APP Iqna</i>", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()
        st.download_button(
            label="📥 Download PDF Hasil",
            data=pdf_buffer,
            file_name="Freight_Calculator_Barge.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
