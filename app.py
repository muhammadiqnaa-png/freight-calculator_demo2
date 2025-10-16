import streamlit as st
import math
from fpdf import FPDF
import pyrebase4 as pyrebase

# ===========================
# KONFIGURASI FIREBASE
# ===========================
firebaseConfig = {
    "apiKey": "GANTI_APIKEY_KAMU",
    "authDomain": "freight-demo2.firebaseapp.com",
    "projectId": "freight-demo2",
    "storageBucket": "freight-demo2.appspot.com",
    "messagingSenderId": "199645170835",
    "appId": "GANTI_APPID_KAMU",
    "databaseURL": ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ===========================
# KONFIGURASI STREAMLIT
# ===========================
st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# ===========================
# LOGIN STATE
# ===========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# ===========================
# HALAMAN LOGIN
# ===========================
def login_page():
    st.title("🔐 Login ke Freight Calculator Barge")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.logged_in = True
            st.session_state.user = email
            st.success("Login berhasil ✅")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal login: {e}")

    st.markdown("---")
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state.show_register = True
        st.rerun()

# ===========================
# HALAMAN REGISTER
# ===========================
def register_page():
    st.title("📝 Daftar Akun Baru")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")

    if st.button("Daftar"):
        if password != confirm:
            st.warning("Password tidak cocok!")
        else:
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Akun berhasil dibuat ✅ Silakan login")
                st.session_state.show_register = False
            except Exception as e:
                st.error(f"Gagal registrasi: {e}")

    if st.button("Kembali ke Login"):
        st.session_state.show_register = False
        st.rerun()

# ===========================
# FUNGSI HITUNG & PDF
# ===========================
def hitung_freight(data):
    sailing_time = (data["distance_pol_pod"] / data["speed_laden"]) + (data["distance_pod_pol"] / data["speed_ballast"])
    total_voyage_days = (sailing_time / 24) + (data["port_stay_pol"] + data["port_stay_pod"])
    total_consumption = (sailing_time * data["consumption_fuel"]) + ((data["port_stay_pol"] + data["port_stay_pod"]) * 120)

    charter_cost = (data["charter_hire"] / 30) * total_voyage_days
    bunker_cost = total_consumption * data["price_bunker"]
    port_cost = data["port_cost_pol"] + data["port_cost_pod"]
    premi_cost = data["distance_pol_pod"] * data["premi"]
    crew_cost = (data["crew_cost"] / 30) * total_voyage_days
    insurance_cost = (data["insurance"] / 30) * total_voyage_days
    docking_saving = (data["docking"] / 30) * total_voyage_days
    maintenance_cost = (data["maintenance"] / 30) * total_voyage_days

    total_cost = sum([charter_cost, bunker_cost, crew_cost, port_cost, premi_cost,
                      data["assist_tug"], insurance_cost, docking_saving, maintenance_cost])

    freight_cost = total_cost / data["qty_cargo"]
    return {
        "sailing_time": sailing_time,
        "total_voyage_days": total_voyage_days,
        "total_consumption": total_consumption,
        "total_cost": total_cost,
        "freight_cost": freight_cost
    }

def generate_pdf(data, results, table_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Freight Calculator Barge", ln=True, align="C")

    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, f"User: {st.session_state.user}", ln=True)
    pdf.cell(200, 8, "", ln=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 8, "Hasil Perhitungan:", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in results.items():
        pdf.cell(200, 8, f"{k.replace('_', ' ').title()}: {v:,.2f}", ln=True)

    pdf.cell(200, 10, "", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 8, "Simulasi Profit 0–50%:", ln=True)

    pdf.set_font("Arial", size=11)
    for row in table_data:
        pdf.cell(200, 8, f"{row['Profit %']}% | Freight: {row['Freight']:,.0f} | Revenue: {row['Revenue']:,.0f} | Profit: {row['Profit']:,.0f}", ln=True)

    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "Generated by Freight Calculator APP Iqna", 0, 0, "C")

    pdf.output("freight_result.pdf")
    return "freight_result.pdf"

# ===========================
# HALAMAN UTAMA
# ===========================
def main_app():
    st.sidebar.success(f"👋 Login sebagai: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    st.title("🚢 Freight Calculator Barge")

    st.sidebar.header("Parameter (Bisa Diedit)")
    data = {
        "speed_laden": st.sidebar.number_input("Speed Laden (knot)", 0.0),
        "speed_ballast": st.sidebar.number_input("Speed Ballast (knot)", 0.0),
        "consumption_fuel": st.sidebar.number_input("Consumption Fuel (liter)", 0.0),
        "price_bunker": st.sidebar.number_input("Price Bunker (Rp/liter)", 0.0),
        "charter_hire": st.sidebar.number_input("Charter Hire/Month (Rp)", 0.0),
        "crew_cost": st.sidebar.number_input("Crew Cost/Month (Rp)", 0.0),
        "insurance": st.sidebar.number_input("Insurance/Month (Rp)", 0.0),
        "docking": st.sidebar.number_input("Docking - Saving/Month (Rp)", 0.0),
        "maintenance": st.sidebar.number_input("Maintenance/Month (Rp)", 0.0),
        "port_cost_pol": st.sidebar.number_input("Port Cost POL (Rp)", 0.0),
        "port_cost_pod": st.sidebar.number_input("Port Cost POD (Rp)", 0.0),
        "assist_tug": st.sidebar.number_input("Assist Tug (Rp)", 0.0),
        "premi": st.sidebar.number_input("Premi (Rp/NM)", 0.0),
        "other_cost": st.sidebar.number_input("Other Cost (Rp)", 0.0),
        "port_stay_pol": st.sidebar.number_input("Port Stay POL (Days)", 0.0),
        "port_stay_pod": st.sidebar.number_input("Port Stay POD (Days)", 0.0),
        "cargo_type": st.selectbox("Type Cargo", ["Pasir (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"]),
        "qty_cargo": st.number_input("QTY Cargo", 0.0),
        "distance_pol_pod": st.number_input("Distance POL - POD (NM)", 0.0),
        "distance_pod_pol": st.number_input("Distance POD - POL (NM)", 0.0),
    }

    if st.button("Hitung Freight"):
        results = hitung_freight(data)
        st.success(f"Total Cost: Rp {results['total_cost']:,.0f}")
        st.info(f"Freight Cost/MT: Rp {results['freight_cost']:,.0f}")

        table_data = []
        for p in range(0, 55, 5):
            freight = results["freight_cost"] * (1 + p/100)
            revenue = freight * data["qty_cargo"]
            pph = revenue * 0.012
            profit = revenue - results["total_cost"] - pph
            table_data.append({"Profit %": p, "Freight": freight, "Revenue": revenue, "Profit": profit})

        st.dataframe(table_data)

        pdf_path = generate_pdf(data, results, table_data)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name="Freight_Report.pdf")

# ===========================
# ROUTING APP
# ===========================
if st.session_state.logged_in:
    main_app()
else:
    if st.session_state.show_register:
        register_page()
    else:
        login_page()

