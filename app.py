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
# Tombol logout di sidebar atas
st.sidebar.markdown("### 👤 Akun")
st.sidebar.write(f"Login sebagai: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Berhasil logout.")
    st.rerun()

st.sidebar.title("⚙️ Parameter Perhitungan")
mode = st.sidebar.radio("Mode Operasi", ["Owner", "Charter"])

# === Gaya sidebar ===
st.markdown("""
    <style>
    section[data-testid="stSidebar"] .stNumberInput label {font-weight:500;}
    section[data-testid="stSidebar"] .stSubheader {color:#2b6cb0;font-weight:700;margin-top:15px;}
    </style>
""", unsafe_allow_html=True)

# ====== SIDEBAR PARAMETER ======
if mode == "Owner":
    st.sidebar.subheader("🚢 Vessel Performance")
    speed_laden = st.sidebar.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("🌊 Speed Ballast (knot)", 0.0)
    consumption = st.sidebar.number_input("⛽ Consumption Fuel (liter/jam)", 0)
    price_fuel = st.sidebar.number_input("💸 Price Fuel (Rp/liter)", 0)
    consumption_fw = st.sidebar.number_input("💧 Consumption Freshwater (Ton/Day)", 0.0)
    price_fw = st.sidebar.number_input("💰 Price Freshwater (Rp/Ton)", 0)
    
    st.sidebar.subheader("🏗️ Fixed Cost (Rp/Month)")
    charter = st.sidebar.number_input("📆 Angsuran (Rp/Month)", 0)
    crew = st.sidebar.number_input("👨‍✈️ Crew cost (Rp/Month)", 0)
    insurance = st.sidebar.number_input("🛡️ Insurance (Rp/Month)", 0)
    docking = st.sidebar.number_input("⚓ Docking - Saving (Rp/Month)", 0)
    maintenance = st.sidebar.number_input("🧰 Maintenance (Rp/Month)", 0)
    certificate = st.sidebar.number_input("📜 Certificate (Rp/Month)", 0)

    st.sidebar.subheader("⚙️ Variable Cost")
    premi_nm = st.sidebar.number_input("📍 Premi (Rp/NM)", 0)
    port_cost_pol = st.sidebar.number_input("🏗️ Port Cost POL (Rp)", 0)
    port_cost_pod = st.sidebar.number_input("🏗️ Port Cost POD (Rp)", 0)
    asist_tug = st.sidebar.number_input("🚤 Asist Tug (Rp)", 0)
    other_cost = st.sidebar.number_input("💼 Other Cost (Rp)", 0)

    st.sidebar.subheader("🕓 Port Stay (Days)")
    port_stay_pol = st.sidebar.number_input("🅿️ POL (Hari)", 0)
    port_stay_pod = st.sidebar.number_input("🅿️ POD (Hari)", 0)

else:  # Charter
    st.sidebar.subheader("🚢 Vessel Performance")
    speed_laden = st.sidebar.number_input("⚓ Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("🌊 Speed Ballast (knot)", 0.0)
    consumption = st.sidebar.number_input("⛽ Consumption Fuel (liter/jam)", 0)
    price_fuel = st.sidebar.number_input("💸 Price Fuel (Rp/liter)", 0)
    consumption_fw = st.sidebar.number_input("💧 Consumption Freshwater (Ton/Day)", 0.0)
    price_fw = st.sidebar.number_input("💰 Price Freshwater (Rp/Ton)", 0)

    st.sidebar.subheader("📊 Voyage Cost")
    charter = st.sidebar.number_input("🚢 Charter hire/Month (Rp)", 0)
    premi_nm = st.sidebar.number_input("📍 Premi (Rp/NM)", 0)
    port_cost_pol = st.sidebar.number_input("🏗️ Port Cost POL (Rp)", 0)
    port_cost_pod = st.sidebar.number_input("🏗️ Port Cost POD (Rp)", 0)
    asist_tug = st.sidebar.number_input("🚤 Asist Tug (Rp)", 0)
    other_cost = st.sidebar.number_input("💼 Other Cost (Rp)", 0)

    st.sidebar.subheader("🕓 Port Stay (Days)")
    port_stay_pol = st.sidebar.number_input("🅿️ POL (Hari)", 0)
    port_stay_pod = st.sidebar.number_input("🅿️ POD (Hari)", 0)

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
        # Sailing & consumption
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        
        # Freshwater
        total_consumption_fw = round(total_voyage_days) * consumption_fw
        freshwater_cost = total_consumption_fw * price_fw
        
        # Costs
        charter_cost = (charter / 30) * total_voyage_days
        bunker_cost = total_consumption * price_fuel
        port_cost = port_cost_pol + port_cost_pod
        premi_cost = distance_pol_pod * premi_nm
        crew_cost = (crew / 30) * total_voyage_days if mode == "Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode == "Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode == "Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode == "Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode == "Owner" else 0

        total_cost = (
            charter_cost + bunker_cost + port_cost + premi_cost + asist_tug +
            crew_cost + insurance_cost + docking_cost + maintenance_cost +
            certificate_cost + freshwater_cost + other_cost
        )

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== TAMPILKAN HASIL =====
        st.subheader("📋 Hasil Perhitungan Utama")
        st.write(f"**⏱️ Sailing Time (Hour)**: {sailing_time:,.2f}")
        st.write(f"**📆 Total Voyage Days**: {total_voyage_days:,.2f}")
        st.write(f"**⛽ Total Fuel Consumption (liter)**: {total_consumption:,.2f}")
        st.write(f"**💧 Total Freshwater Consumption (Ton)**: {total_consumption_fw:,.2f}")
        st.write(f"**💰 Freshwater Cost (Rp)**: {freshwater_cost:,.2f}")
        if mode == "Owner":
            st.write(f"**📜 Certificate Cost (Rp)**: {certificate_cost:,.2f}")
        st.write(f"**💰 Total Cost (Rp)**: {total_cost:,.2f}")
        st.write(f"**💵 Freight Cost (Rp/{type_cargo.split()[1]})**: {freight_cost_mt:,.2f}")

        # ===== TABEL PROFIT =====
        data = []
        for p in range(0, 55, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"{freight_persen:,.2f}", f"{revenue:,.2f}", f"{pph:,.2f}", f"{profit:,.2f}"])

        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.subheader("📊 Tabel Profit 0% - 50%")
        st.dataframe(df_profit)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
