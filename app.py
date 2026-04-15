import streamlit as st
import math
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
import requests
import streamlit as st

# ==========================================================
# ⚙️ Page Config (WAJIB paling atas!)
# ==========================================================
st.set_page_config(
    page_title="Freight Calculator Barge",
    page_icon="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/icon-512x512.png",
    layout="wide"
)
st.markdown("""
<style>
.card {
    background: linear-gradient(145deg, #1f2937, #111827);
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 🔧 PWA Support — biar bisa di-install di HP
# ==========================================================
st.markdown("""
<link rel="manifest" href="https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/manifest.json">
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('https://raw.githubusercontent.com/muhammadiqnaa-png/freight-calculator/main/service-worker.js')
    .then(reg => console.log("Service worker registered:", reg))
    .catch(err => console.log("Service worker failed:", err));
}
</script>
""", unsafe_allow_html=True)

# ==========================================================
# 🍎 iPhone (Safari) Support — tambahan meta
# ==========================================================
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="FreightCalc">
""", unsafe_allow_html=True)


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

# ===== LOGIN =====
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
        email = st.text_input("Email Register")
        password = st.text_input("Password Register", type="password")
        if st.button("Register 📝"):
            ok, data = register_user(email, password)
            if ok:
                st.success("Registration successful! Please login.")
            else:
                st.error("Failed to register. Email may already exist.")
    st.stop()

cargo_capacity = {
    "270 ft": {
        "Coal (MT)": 5500,
        "Nickel (MT)": 5500,
        "Bauxite (MT)": 5500,
        "Sand (M3)": 3500,
        "Split (M3)": 3500
    },
    "300 ft": {
        "Coal (MT)": 7500,
        "Nickel (MT)": 7500,
        "Bauxite (MT)": 7500,
        "Sand (M3)": 4300,
        "Split (M3)": 4300
    },
    "330 ft": {
        "Coal (MT)": 11500,
        "Nickel (MT)": 11500,
        "Bauxite (MT)": 11500,
        "Sand (M3)": 5500,
        "Split (M3)": 6500
    }
}
    
# ===== MASTER ROUTE =====
if "distance_data" not in st.session_state:
    st.session_state.distance_data = [
        {"pol": "SIP, Kuala Cenaku", "pod": "Muara Bangkong", "distance": 80},
        {"pol": "SIP, Kuala Cenaku", "pod": "Bangka", "distance": 275},
        {"pol": "SIP, Kuala Cenaku", "pod": "Merak", "distance": 475},
        {"pol": "SIP, Kuala Cenaku", "pod": "Lontar", "distance": 490},
        {"pol": "SIP, Kuala Cenaku", "pod": "Labuan", "distance": 515},
        {"pol": "SIP, Kuala Cenaku", "pod": "Indramayu", "distance": 525},
        {"pol": "SIP, Kuala Cenaku", "pod": "Pangkalan Susu", "distance": 540},
        {"pol": "SIP, Kuala Cenaku", "pod": "Pelabuhan Ratu", "distance": 640},
        {"pol": "SIP, Kuala Cenaku", "pod": "Rembang", "distance": 690},
        {"pol": "KBS, Kuala Tungkal", "pod": "Suralaya", "distance": 475},
        {"pol": "KBS, Kuala Tungkal", "pod": "Labuan", "distance": 505},
        {"pol": "KBS, Kuala Tungkal", "pod": "Pangkalan Susu", "distance": 555},
        {"pol": "PUS, Jambi", "pod": "Muara Sabak", "distance": 95},
        {"pol": "PUS, Jambi", "pod": "Belitung", "distance": 320},
        {"pol": "PUS, Jambi", "pod": "Banten", "distance": 435},
        {"pol": "PUS, Jambi", "pod": "Suralaya", "distance": 435},
        {"pol": "PUS, Jambi", "pod": "Lontar", "distance": 450},
        {"pol": "PUS, Jambi", "pod": "Labuan", "distance": 465},
        {"pol": "PUS, Jambi", "pod": "Indramayu", "distance": 485},
        {"pol": "PUS, Jambi", "pod": "Rembang", "distance": 650},
        {"pol": "PUS, Jambi", "pod": "Awar Awar", "distance": 685},
        {"pol": "EWF, Jambi", "pod": "Ketapang", "distance": 425},
        {"pol": "EWF, Jambi", "pod": "Ketapang", "distance": 425},
        {"pol": "EWF, Jambi", "pod": "Lontar", "distance": 445},
        {"pol": "EWF, Jambi", "pod": "Indramayu", "distance": 485},
        {"pol": "EWF, Jambi", "pod": "Pangkalan Susu", "distance": 565},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Tanjung Kampeh", "distance": 60},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Merak", "distance": 325},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Lontar", "distance": 335},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Marunda", "distance": 345},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Indramayu", "distance": 375},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Perawang", "distance": 425},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Pelabuhan Ratu", "distance": 485},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Rembang", "distance": 545},
        {"pol": "Tempirai, Sungai Lilin", "pod": "Awar Awar", "distance": 575},
        {"pol": "SBL, Palembang", "pod": "Tanjung Kampeh", "distance": 100},
        {"pol": "SBL, Palembang", "pod": "Marunda", "distance": 385},
        {"pol": "SBL, Palembang", "pod": "BAP, Kendawangan", "distance": 435},
        {"pol": "SBL, Palembang", "pod": "WHW, Kendawangan", "distance": 440},
        {"pol": "SBL, Palembang", "pod": "Cemindo, Bayah", "distance": 525},
        {"pol": "SDJ, Palembang", "pod": "Bangka", "distance": 210},
        {"pol": "SDJ, Palembang", "pod": "MEI, Banten", "distance": 365},
        {"pol": "SDJ, Palembang", "pod": "Ciwandan", "distance": 370},
        {"pol": "SDJ, Palembang", "pod": "Cirebon", "distance": 460},
        {"pol": "WBS, Palembang", "pod": "WHW, Kendawangan", "distance": 405},
        {"pol": "Tarahan, Lampung", "pod": "Suralaya", "distance": 60},
        {"pol": "Tarahan, Lampung", "pod": "Cemindo, Bayah", "distance": 155},
        {"pol": "Tarahan, Lampung", "pod": "Indramayu", "distance": 185},
        {"pol": "Tarahan, Lampung", "pod": "Awar Awar", "distance": 430},
        {"pol": "Tarahan, Lampung", "pod": "Pacitan", "distance": 480},
        {"pol": "Lampung, Muara Teladas", "pod": "Marunda", "distance": 125},
        {"pol": "Hasnur Pendang, Kalteng", "pod": "Celukan Bawang", "distance": 475},
        {"pol": "Hasnur Pendang, Kalteng", "pod": "Marunda", "distance": 705},
        {"pol": "Hasnur Pendang, Kalteng", "pod": "Indramayu", "distance": 635},
        {"pol": "Hasnur Pendang, Kalteng", "pod": "Merak", "distance": 755},
        {"pol": "Hasnur Pendang, Kalteng", "pod": "Cirebon", "distance": 600},
        {"pol": "Hasnur Pendang, Kalteng", "pod": "Gresik", "distance": 435},
        {"pol": "Talenta, Sungai Putting", "pod": "Taboneo", "distance": 60},
        {"pol": "Talenta, Sungai Putting", "pod": "Gresik", "distance": 295},
        {"pol": "Talenta, Sungai Putting", "pod": "BAI, Bintan", "distance": 725},
        {"pol": "MBL, Samarinda", "pod": "Southport, Klang Malaysia", "distance": 1435},
        {"pol": "ABN, Samarinda", "pod": "Cirebon", "distance": 710},
        {"pol": "Kideco, Grogot", "pod": "Tanjung Kasam, Batam", "distance": 995},
        {"pol": "TIA, Bunati", "pod": "Ciwandan", "distance": 610},
        {"pol": "BIB, Bunati", "pod": "Jawa 7", "distance": 605},
        {"pol": "SPJ, Suralaya", "pod": "Lontar", "distance": 35},
        {"pol": "SPJ, Suralaya", "pod": "Labuan", "distance": 40},
        {"pol": "SPJ, Suralaya", "pod": "Pelabuhan Ratu", "distance": 165},
    ]

# ==========================================================
# ⚙️ PRESET PARAMETER KAPAL (non-intrusive)
# - ditaruh di expander sidebar yang default tertutup
# - tidak mengubah layout main / posisi expander lain
# ==========================================================
preset_params = {
    "270 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 85, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 40000000,
        "docking": 40000000, "maintenance": 40000000,
        "certificate": 40000000, "premi_nm": 50000, "other_cost": 10000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 4, "port_stay_pod": 4
    },
    "300 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 115, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 50000000,
        "docking": 50000000, "maintenance": 50000000,
        "certificate": 45000000, "premi_nm": 50000, "other_cost": 15000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    },
    "330 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 130, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 60000000,
        "docking": 60000000, "maintenance": 60000000,
        "certificate": 50000000, "premi_nm": 50000, "other_cost": 20000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    },
     "Custom": {
        "speed_laden": 0, "speed_ballast": 0,
        "consumption": 0, "price_fuel": 0,
        "consumption_fw": 0, "price_fw": 0,
        "charter": 0, "crew": 0, "insurance": 0,
        "docking": 0, "maintenance": 0,
        "certificate": 0, "premi_nm": 0, "other_cost": 0,
        "port_cost_pol": 0, "port_cost_pod": 0, "asist_tug": 0,
        "port_stay_pol": 0, "port_stay_pod": 0
    }
}


if "history_calculate" not in st.session_state:
    st.session_state.history_calculate = []

# =========================
# ⚙️ SETUP
# =========================
with st.sidebar.expander("⚙️ Setup", expanded=True):

    mode = st.selectbox("Mode", ["Owner", "Charter"])

# ===== INIT PRESET STATE =====
if "preset_selected" not in st.session_state:
    st.session_state.preset_selected = "Custom"

# Handler
def update_preset():
    st.session_state.preset_selected = st.session_state.preset_control
    st.session_state.apply_preset = True

# =========================
# 🚢 VOYAGE INPUT
# =========================
with st.sidebar.expander("🚢 Voyage Input", expanded=False):

    with st.expander("➕ Add Distance", expanded=False):

        col1, col2 = st.columns(2)

        with col1:
            pol_input = st.text_input("POL", key="md_pol")

        with col2:
            pod_input = st.text_input("POD", key="md_pod")

        distance_input = st.number_input("Distance (NM)", 0.0, key="md_distance")

        if st.button("💾 Save Distance"):
            if pol_input and pod_input:
                st.session_state.distance_data.append({
                    "pol": pol_input.strip().upper(),
                    "pod": pod_input.strip().upper(),
                    "distance": distance_input
                })
                st.success("Distance saved!")

if st.session_state.get("apply_preset", False):
    if st.session_state.preset_selected in preset_params:
        selected = preset_params[st.session_state.preset_selected]

        for key, value in selected.items():
            st.session_state[key] = value

    st.session_state.apply_preset = False

# =========================
# 📊 PARAMETER
# =========================
with st.sidebar.expander("📊 Parameter", expanded=False):

    # ===== SIZE BARGE =====
    st.markdown("### 🚢 Size Barge")

    preset = st.segmented_control(
        "Pilih Size",
        ["270 ft", "300 ft", "330 ft", "Custom"],
        default=st.session_state.preset_selected,
        key="preset_control",
        on_change=update_preset
    )

    # ===== SPEED =====
    with st.expander("🚢 Speed"):
        for label, key in [
            ("Speed Laden (knot)", "speed_laden"),
            ("Speed Ballast (knot)", "speed_ballast"),
        ]:
            st.number_input(label, step=0.1, format="%.1f", key=key)

        speed_laden = st.session_state.speed_laden
        speed_ballast = st.session_state.speed_ballast

    # ===== FUEL =====
    with st.expander("⛽ Fuel"):
        consumption = st.number_input(
            "Consumption Fuel (liter/hour)",
            value=st.session_state.get("consumption", 0),
            key="consumption"
        )

        price_fuel = st.number_input(
            "Price Fuel (Rp/Ltr)",
            value=st.session_state.get("price_fuel", 0),
            key="price_fuel"
        )
    
    # ===== FRESHWATER =====
    with st.expander("💧 Freshwater"):
        consumption_fw = st.number_input(
            "Consumption Freshwater (Ton/Day)",
            value=st.session_state.get("consumption_fw", 0)
        )
        price_fw = st.number_input(
            "Price Freshwater (Rp/Ton)",
            value=st.session_state.get("price_fw", 0)
        )

    # ===== OWNER / CHARTER =====
    if mode == "Owner":
        with st.expander("🏗️ Owner Cost"):
            charter = st.number_input("Angsuran (Rp/Month)", value=st.session_state.get("charter", 0))
            crew = st.number_input("Crew (Rp/Month)", value=st.session_state.get("crew", 0))
            insurance = st.number_input("Insurance (Rp/Month)", value=st.session_state.get("insurance", 0))
            docking = st.number_input("Docking (Rp/Month)", value=st.session_state.get("docking", 0))
            maintenance = st.number_input("Maintenance (Rp/Month)", value=st.session_state.get("maintenance", 0))
            certificate = st.number_input("Certificate (Rp/Month)", value=st.session_state.get("certificate", 0))
            premi_nm = st.number_input("Premi (Rp/NM)", value=st.session_state.get("premi_nm", 0))
            other_cost = st.number_input("Other Cost (Rp)", value=st.session_state.get("other_cost", 0))
    else:
        with st.expander("🏗️ Charter Cost"):
            charter = st.number_input("Charter Hire (Rp/Month)", value=st.session_state.get("charter", 0))
            premi_nm = st.number_input("Premi (Rp/NM)", value=st.session_state.get("premi_nm", 0))
            other_cost = st.number_input("Other Cost (Rp)", value=st.session_state.get("other_cost", 0))

    # ===== PORT COST =====
    with st.expander("⚓ Port Cost"):
        port_cost_pol = st.number_input("Port Cost POL (Rp)", value=st.session_state.get("port_cost_pol", 0))
        port_cost_pod = st.number_input("Port Cost POD (Rp)", value=st.session_state.get("port_cost_pod", 0))
        asist_tug = st.number_input("Asist Tug (Rp)", value=st.session_state.get("asist_tug", 0))

    # ===== GENERAL OVERHEAD =====
    with st.expander("🏢 General Overhead"):
        opex_office = st.number_input("Opex (Rp/Month)", value=st.session_state.get("opex_office", 0))
        depreciation_kapal = st.number_input("Depreciation Kapal (Rp/Month)", value=st.session_state.get("depreciation_kapal", 0))

    # ===== PORT STAY =====
    with st.expander("🕓 Port Stay"):
        port_stay_pol = st.number_input("POL (Days)", value=st.session_state.get("port_stay_pol", 0))
        port_stay_pod = st.number_input("POD (Days)", value=st.session_state.get("port_stay_pod", 0))

    # ===== ADDITIONAL COST =====
    with st.expander("➕ Additional Cost"):

        if "additional_costs" not in st.session_state:
            st.session_state.additional_costs = []

        add_new = st.button("➕ Add Additional Cost")
        if add_new:
            st.session_state.additional_costs.append({
                "name": "",
                "price": 0,
                "unit": "Ltr",
                "subtype": "Day",
                "consumption": 0
            })

        updated_costs = []
        unit_options = ["Ltr", "Ton", "Month", "Voyage", "MT", "M3", "Day"]

        for i, cost in enumerate(st.session_state.additional_costs):
            st.markdown(f"*Additional Cost {i+1}*")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(f"Name {i+1}", cost.get("name", ""), key=f"name_{i}")
                price = st.number_input(f"Price {i+1} (Rp)", cost.get("price", 0), key=f"price_{i}")

            with col2:
                unit = st.selectbox(
                    f"Unit {i+1}",
                    unit_options,
                    index=unit_options.index(cost.get("unit", "Ltr")) if cost.get("unit", "Ltr") in unit_options else 0,
                    key=f"unit_{i}"
                )

                subtype = "Day"
                if unit in ["Ltr", "Ton"]:
                    subtype = st.selectbox(
                        f"Type {i+1}",
                        ["Day", "Hour"],
                        index=["Day", "Hour"].index(cost.get("subtype", "Day")),
                        key=f"subtype_{i}"
                    )

                additional_consumption = 0
                if unit in ["Ltr", "Ton"]:
                    additional_consumption = st.number_input(
                        f"Consumption {i+1} ({unit}/{subtype})",
                        cost.get("consumption", 0),
                        key=f"additional_consumption_{i}"
                    )

            remove = st.button(f"❌ Remove {i+1}", key=f"remove_{i}")

            if not remove:
                updated_costs.append({
                    "name": name,
                    "price": price,
                    "unit": unit,
                    "subtype": subtype,
                    "consumption": additional_consumption
                })

        st.session_state.additional_costs = updated_costs

# =========================
# 📂 MASTER DATA
# =========================

with st.sidebar.expander("📂 Master Data", expanded=False):

    # =========================
    # 📋 LIST DISTANCE (SUB)
    # =========================
    with st.expander("📋 List Distance", expanded=False):

        if len(st.session_state.distance_data) > 1:
            df_distance = pd.DataFrame(st.session_state.distance_data)
            df_distance.index = df_distance.index + 1
            st.dataframe(df_distance, use_container_width=True, height=200)

            delete_index = st.number_input(
                "Hapus index",
                min_value=1,
                max_value=len(df_distance)-1,
                step=1
            )

            if st.button("❌ Delete Selected"):
                st.session_state.distance_data.pop(delete_index - 1)
                st.rerun()
        else:
            st.caption("Belum ada data distance")

    # =========================
    # 📜 HISTORY CALCULATE (SUB)
    # =========================
    with st.expander("📜 History Calculate", expanded=False):

        if len(st.session_state.history_calculate) == 0:
            st.caption("Belum ada history")
        else:
            history_limit = st.number_input(
                "Tampilkan terakhir",
                1, 20, 5
            )

            history_data = list(reversed(st.session_state.history_calculate))[:history_limit]

            for i, item in enumerate(history_data):
                with st.expander(f"📄 {item['name']}"):
                    st.download_button(
                        label="⬇️ Download",
                        data=item["data"],
                        file_name=item["name"],
                        mime="application/pdf",
                        key=f"history_{i}"
                    )

            if st.button("🗑️ Clear History"):
                st.session_state.history_calculate = []
                st.rerun()

with st.sidebar.expander("👤 Account", expanded=True):

    st.write(f"📧 {st.session_state.email}")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.success("Successfully logged out.")
        st.rerun()

# ===== MAIN INPUT =====
st.markdown("""
<h1 style='margin-bottom:0;'>🚢 Freight Calculator</h1>
<p style='color:gray; margin-top:0;'>Professional Barge Cost & Profit Analysis</p>
<hr>
""", unsafe_allow_html=True)

# ambil data dari master route
pol_list = sorted(list(set([r["pol"] for r in st.session_state.distance_data])))
pod_list = sorted(list(set([r["pod"] for r in st.session_state.distance_data])))

col1, col2, col3 = st.columns(3)

with col1:
    port_pol = st.selectbox("Port Of Loading", pol_list)

with col2:
    port_pod = st.selectbox("Port Of Discharge", pod_list)

with col3:
    next_port = st.selectbox(
        "Next Port (Optional)",
        [None] + pol_list,
        format_func=lambda x: "Pilih (Optional)" if x is None else x
    )

# ===== AUTO DISTANCE =====
distance_pol_pod = 0
distance_pod_next = 0

for r in st.session_state.distance_data:

    # POL → POD
    if r["pol"] == port_pol and r["pod"] == port_pod:
        distance_pol_pod = r["distance"]

    # POD → NEXT
    if next_port and r["pol"] == port_pod and r["pod"] == next_port:
        distance_pod_next = r["distance"]

# auto reverse (NEXT → POD)
if next_port and distance_pod_next == 0:
    for r in st.session_state.distance_data:
        if r["pol"] == next_port and r["pod"] == port_pod:
            distance_pod_next = r["distance"]

# tampilkan
col1, col2 = st.columns(2)

with col1:
    st.number_input(
        "Distance POL → POD (NM)",
        value=distance_pol_pod,
        disabled=True
    )

with col2:
    if next_port:
        st.number_input(
            "Distance POD → Next (NM)",
            value=distance_pod_next,
            disabled=True
        )
    else:
        st.empty()

# validasi
if distance_pol_pod == 0:
    st.error(f"❌ Distance {port_pol} → {port_pod} belum ada di master data!")

if next_port and distance_pod_next == 0:
    st.error(f"❌ Distance {port_pod} → {next_port} belum ada di master data!")

# stop hanya kalau data wajib kosong
if distance_pol_pod == 0:
    st.stop()

if next_port and distance_pod_next == 0:
    st.stop()


# ===== TYPE CARGO =====
type_cargo = st.selectbox(
    "Type Cargo",
    ["Bauxite (MT)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"],
    key="type_cargo"
)

# ===== DEFAULT QTY =====
default_qty = 0
if st.session_state.preset_selected in cargo_capacity:
    default_qty = cargo_capacity[st.session_state.preset_selected].get(type_cargo, 0)

# ===== INIT SESSION (HANYA SEKALI) =====
if "qyt_cargo" not in st.session_state:
    st.session_state.qyt_cargo = default_qty

# ===== UPDATE HANYA KALAU SIZE / CARGO BERUBAH =====
if (
    "last_preset" not in st.session_state or
    "last_cargo" not in st.session_state or
    st.session_state.last_preset != st.session_state.preset_selected or
    st.session_state.last_cargo != type_cargo
):
    st.session_state.qyt_cargo = default_qty

# simpan kondisi terakhir
st.session_state.last_preset = st.session_state.preset_selected
st.session_state.last_cargo = type_cargo

# ===== INPUT (BISA DIEDIT) =====
qyt_cargo = st.number_input(
    "Cargo Quantity",
    value=st.session_state.qyt_cargo,
    key="qyt_cargo"
)

freight_price_input = st.number_input("Freight Price (Rp/MT)", 0)

# ===== PERHITUNGAN =====
if st.button("🚀 Calculate Freight", use_container_width=True):
    try:
        # Waktu sailing (hour) based on speed inputs (hours)
        sailing_time = (
            (distance_pol_pod / speed_laden) +
            ((distance_pod_next / speed_ballast) if next_port else 0)
        )
        # total voyage in days (sailing hours converted to days + port stays)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days % 1 < 0.5 else int(total_voyage_days) + 1

        # consumptions
        total_consumption_fuel = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_round
        cost_fw = total_consumption_fw * price_fw
        cost_fuel = total_consumption_fuel * price_fuel

        # core costs
        charter_cost = (charter / 30) * total_voyage_days
        crew_cost = (crew / 30) * total_voyage_days if mode == "Owner" else 0
        insurance_cost = (insurance / 30) * total_voyage_days if mode == "Owner" else 0
        docking_cost = (docking / 30) * total_voyage_days if mode == "Owner" else 0
        maintenance_cost = (maintenance / 30) * total_voyage_days if mode == "Owner" else 0
        certificate_cost = (certificate / 30) * total_voyage_days if mode == "Owner" else 0
        total_general_overhead = ((opex_office + depreciation_kapal) / 30) * total_voyage_days
        premi_cost = distance_pol_pod * premi_nm
        port_cost = port_cost_pol + port_cost_pod + asist_tug

        # ===== ADDITIONAL COST CALCULATION =====
        additional_total = 0
        additional_breakdown = {}

        for cost in st.session_state.get("additional_costs", []):
            name = cost.get("name", "")
            unit = cost.get("unit", "")
            subtype = cost.get("subtype", "Day")
            price = cost.get("price", 0)
            cons = cost.get("consumption", 0)

            val = 0
            if unit == "Ltr":
                if subtype == "Day":
                    val = cons * total_voyage_days * price
                elif subtype == "Hour":
                    val = cons * (total_voyage_days * 24) * price
            elif unit == "Ton":
                if subtype == "Day":
                    val = cons * total_voyage_days * price
                elif subtype == "Hour":
                    val = cons * (total_voyage_days * 24) * price
            elif unit == "Month":
                val = (price / 30) * total_voyage_days
            elif unit == "Voyage":
                val = price
            elif unit in ["MT", "M3"]:
                val = price * qyt_cargo
            elif unit == "Day":
                val = price * total_voyage_days

            if val and val > 0:
                key_name = name if name else f"{unit} cost"
                if key_name in additional_breakdown:
                    additional_breakdown[key_name] += val
                else:
                    additional_breakdown[key_name] = val
                additional_total += val

        # ===== TOTAL COST FINAL =====
        total_cost = sum([
            charter_cost, crew_cost, insurance_cost, docking_cost, maintenance_cost, certificate_cost,total_general_overhead, 
            premi_cost, port_cost, cost_fuel, cost_fw, other_cost, additional_total
        ])

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

        # ===== REVENUE CALC =====
        revenue_user = freight_price_input * qyt_cargo
        pph_user = revenue_user * 0.012
        profit_user = revenue_user - total_cost - pph_user
        profit_percent_user = (profit_user / total_cost * 100) if total_cost > 0 else 0

        # ===== TCE CALCULATION =====
        tce_base_cost = cost_fuel + cost_fw + port_cost + premi_cost

        tce_per_day = (
            tce_base_cost / total_voyage_days
            if total_voyage_days > 0 else 0
        )

        tce_per_month = tce_per_day * 30

        st.markdown("## 📊 Summary")

        # ===== TOP KPI =====
        col1, col2, col3 = st.columns(3)

        col1.metric("🚢 Voyage Days", f"{total_voyage_days:.2f}")
        col2.metric("💰 Total Cost", f"Rp {total_cost:,.0f}")
        col3.metric("📦Freight Cost", f"Rp {freight_cost_mt:,.0f} / {type_cargo.split()[1]}")

        st.divider()

        # ===== OPERATIONAL =====
        st.markdown("### ⚙️ Operational")

        col1, col2, col3 = st.columns(3)
        col1.metric("⏱️ Sailing Time", f"{sailing_time:.1f} Hrs")
        col2.metric("⛽ Fuel", f"{total_consumption_fuel:,.0f} Ltr")
        col3.metric("💧 Freshwater", f"{total_consumption_fw:,.0f} Ton")

        st.divider()

        # ===== DEFINE OWNER / CHARTER DATA =====
        if mode == "Owner":
            owner_data = {
                "Angsuran": charter_cost,
                "Crew": crew_cost,
                "Insurance": insurance_cost,
                "Docking": docking_cost,
                "Maintenance": maintenance_cost,
                "Certificate": certificate_cost,
                "Premi": premi_cost,
                "Port Cost": port_cost,
                "Other Cost": other_cost
            }
        else:
            owner_data = {
                "Charter Hire": charter_cost,
                "Premi": premi_cost,
                "Port Cost": port_cost,
                "Other Cost": other_cost
            }
        
        # ===== COST BREAKDOWN =====
        st.markdown("### 🏗️ Cost Breakdown")

        cost_dict = owner_data.copy()
        cost_dict["Fuel"] = cost_fuel
        cost_dict["Freshwater"] = cost_fw
        cost_dict["General Overhead"] = total_general_overhead

        df_cost = pd.DataFrame(list(cost_dict.items()), columns=["Item", "Amount"])
        df_cost["Amount"] = df_cost["Amount"].apply(lambda x: f"Rp {x:,.0f}")

        st.dataframe(df_cost, use_container_width=True, hide_index=True)

        # ===== ADDITIONAL =====
        if additional_breakdown:
            st.markdown("### ➕ Additional Costs")
            df_add = pd.DataFrame(list(additional_breakdown.items()), columns=["Item", "Amount"])
            df_add["Amount"] = df_add["Amount"].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(df_add, use_container_width=True, hide_index=True)

        st.divider()

        # ===== PROFIT =====
        st.markdown("### 💰 Profit Analysis")
        
        col1, col2, col3 = st.columns(3)

        col1.metric("Revenue", f"Rp {revenue_user:,.0f}")
        profit_color = "normal"
        if profit_user > 0:
            profit_color = "normal"
        else:
            profit_color = "inverse"
        col2.metric("Profit", f"Rp {profit_user:,.0f}", delta=None)
        col3.metric("Profit %", f"{profit_percent_user:.2f}%")

        # warna indikator
        if profit_user > 0:
            st.success("🟢 Profitable Voyage")
        else:
            st.error("🔴 Loss Voyage")
            
        st.divider()

        # ===== TCE =====
        st.markdown("### ⏱️ TCE")

        col1, col2 = st.columns(2)
        col1.metric("Per Day", f"Rp {tce_per_day:,.0f}")
        col2.metric("Per Month", f"Rp {tce_per_month:,.0f}")

        st.divider()

        # ===== PROFIT SCENARIO =====
        data = []
        for p in range(0, 80, 5):
            freight_persen = freight_cost_mt * (1 + p / 100)
            revenue = freight_persen * qyt_cargo
            pph = revenue * 0.012
            gross_profit = revenue - total_cost - pph
            data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {gross_profit:,.0f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Gross Profit (Rp)"])

        st.subheader("💹 Profit Scenario 0–75%")
        st.dataframe(df_profit, use_container_width=True)

        # ===== PDF GENERATOR =====
        def create_pdf(username):
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=25,
                leftMargin=25,
                topMargin=0,
                bottomMargin=0
            )

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='HeaderBlue', fontSize=16, textColor=colors.HexColor("#0d47a1"), alignment=1, spaceAfter=4))
            styles.add(ParagraphStyle(name='SubHeader', fontSize=12, textColor=colors.HexColor("#0d47a1"), spaceAfter=4, fontName='Helvetica-Bold'))
            styles.add(ParagraphStyle(name='NormalSmall', fontSize=8, leading=12))
            styles.add(ParagraphStyle(name='Bold', fontSize=11, fontName='Helvetica-Bold'))

            elements = []
            def fmt_rp(x):
                return f"Rp {x:,.0f}"

            def pct_of_total(x):
                try:
                    if total_cost and total_cost > 0:
                        return f"   ({(x / total_cost) * 100:.1f}%)"
                    else:
                        return " (0.0%)"
                except Exception:
                    return " (0.0%)"

            # ===== HEADER =====
            title = Paragraph("<b>Freight Calculation Report</b>", styles['HeaderBlue'])
            elements.append(title)
            elements.append(Spacer(1, 2))

            # ===== VOYAGE INFO =====
            elements.append(Paragraph("Voyage Information", styles['SubHeader']))
            voyage_data = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Next Port", next_port],
                ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod:,.0f}"],
                ["Total Voyage (Days)", f"{total_voyage_days:.2f}"],
            ]
            t_voyage = Table(voyage_data, colWidths=[9*cm, 9*cm])
            t_voyage.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_voyage, Spacer(1, 4)]

            # ===== OPERATIONAL COST =====
            elements.append(Paragraph("Operational & Cost Summary", styles['SubHeader']))
            calc_data = [
                ["Total Sailing Time (Hour)", f"{sailing_time:.2f}"],
                ["Total Consumption Fuel (Ltr)", f"{total_consumption_fuel:,.0f}"],
                ["Total Consumption Freshwater (Ton)", f"{total_consumption_fw:,.0f}"],
                ["Fuel Cost (Rp)", f"{fmt_rp(cost_fuel)}{pct_of_total(cost_fuel)}"],
                ["Freshwater Cost (Rp)", f"{fmt_rp(cost_fw)}{pct_of_total(cost_fw)}"],
                ["Total General Overhead (Voyage)", fmt_rp(total_general_overhead) + pct_of_total(total_general_overhead)],
            ]

            for k, v in owner_data.items():
                calc_data.append([k, f"{fmt_rp(v)}{pct_of_total(v)}"])

            if additional_breakdown:
                calc_data.append(["--- Additional Costs ---", ""])
                for k, v in additional_breakdown.items():
                    calc_data.append([k, f"{fmt_rp(v)}{pct_of_total(v)}"])

            calc_data.append(["Total Cost (Rp)", f"Rp {total_cost:,.0f}"])
            calc_data.append([f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"])

            t_calc = Table(calc_data, colWidths=[9*cm, 9*cm])
            t_calc.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_calc, Spacer(1, 4)]

            # ===== FREIGHT PRICE =====
            if freight_price_input > 0:
                elements.append(Paragraph("Freight Price Calculation User", styles['SubHeader']))
                fpc_data = [
                    ["Freight Price (Rp/MT)", f"Rp {freight_price_input:,.0f}"],
                    ["Revenue", f"Rp {revenue_user:,.0f}"],
                    ["PPH 1.2%", f"Rp {pph_user:,.0f}"],
                    ["Profit", f"Rp {profit_user:,.0f}"],
                    ["Profit %", f"{profit_percent_user:.2f} %"],
                ]
                t_fpc = Table(fpc_data, colWidths=[9*cm, 9*cm])
                t_fpc.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                ]))
                elements += [t_fpc, Spacer(1, 4)]

            # ===== TCE =====
            elements.append(Paragraph("Time Charter Equivalent (TCE)", styles['SubHeader']))

            tce_data = [
                ["Base Cost (Fuel + FW + Port + Premi)", fmt_rp(tce_base_cost)],
                ["TCE Per Day", f"{fmt_rp(tce_per_day)} / Day"],
                ["TCE Per Month", f"{fmt_rp(tce_per_month)} / Month"],
            ]

            t_tce = Table(tce_data, colWidths=[9*cm, 9*cm])
            t_tce.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))

            elements += [t_tce, Spacer(1, 4)]


            # ===== PROFIT SCENARIO =====
            elements.append(Paragraph("Profit Scenario 0–75%", styles['SubHeader']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, colWidths=[3*cm, 3.8*cm, 3.8*cm, 3.8*cm, 3.8*cm])
            t_profit.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements += [t_profit, Spacer(1, 4)]

            elements.append(Spacer(1, 10))

            note_text = f"""
            <b>Note:</b><br/>
            - Speed Laden : {speed_laden} knot<br/>
            - Speed Ballast : {speed_ballast} knot<br/>
            - Fuel Price : Rp {price_fuel:,.0f} / Ltr<br/>
            - Port Stay POL : {port_stay_pol} Days<br/>
            - Port Stay POD : {port_stay_pod} Days
            """

            elements.append(Paragraph(note_text, styles['NormalSmall']))
            elements.append(Spacer(1, 6))

            # ===== FOOTER =====
            footer_text = f"Generated by {username} | https://freight-calculator-app.streamlit.app/"
            elements.append(Paragraph(footer_text, styles['NormalSmall']))

            # Tanggal generated di bawah footer
            generated_date = Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", styles['NormalSmall'])
            elements.append(generated_date)

            # ===== BUILD PDF =====
            doc.build(elements)
            buffer.seek(0)
            return buffer

        # ===== GENERATE PDF & DOWNLOAD BUTTON =====
        pdf_buffer = create_pdf(username=st.session_state.email)
        file_name = f"Freight Report {port_pol} - {port_pod} {datetime.now():%Y%m%d}.pdf"
        pdf_bytes = pdf_buffer.getvalue()

        st.session_state.history_calculate.append({
            "name": file_name,
            "data": pdf_bytes
        })

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error: {e}")
