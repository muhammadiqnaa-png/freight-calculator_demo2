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

# ========== FIREBASE AUTH ==========
API_KEY = st.secrets["FIREBASE_API_KEY"]

def signup(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json() if res.status_code == 200 else None

def login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json() if res.status_code == 200 else None

# ========== LOGIN PAGE ==========
def login_page():
    st.title("🚢 Freight Calculator Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email, password)
        if user:
            st.session_state.user = user["email"]
            st.success("Login berhasil ✅")
            st.rerun()
        else:
            st.error("Email atau password salah")

    st.write("---")
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state.page = "register"
        st.rerun()

# ========== REGISTER PAGE ==========
def register_page():
    st.title("📝 Daftar Akun Baru")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Daftar"):
        user = signup(email, password)
        if user:
            st.success("Akun berhasil dibuat! Silakan login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Gagal membuat akun. Coba email lain.")

    if st.button("⬅️ Kembali ke Login"):
        st.session_state.page = "login"
        st.rerun()

# ========== LOGOUT BAR ==========
def user_bar():
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; background-color:#f0f2f6; padding:10px 20px; border-radius:8px;">
            <div>👋 Logged in as: <b>{st.session_state['user']}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    logout_clicked = st.button("Logout", key="logout_btn")
    if logout_clicked:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ========== MAIN APP ==========
def main_app():
    user_bar()
    st.title("🚢 Freight Calculator Barge")

    mode = st.sidebar.radio("Pilih Mode:", ["Owner", "Charter"])
    st.sidebar.title("⚙️ Parameter (Bisa Diedit)")

    # ===== INPUT DASAR =====
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0)
    consumption = st.sidebar.number_input("Consumption Fuel (liter)", 0)
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0)
    premi_nm = st.sidebar.number_input("Premi (Rp/NM)", 0)
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", 0)
    other_cost = st.sidebar.number_input("Other Cost (Rp)", 0)

    if mode == "Owner":
        charter = st.sidebar.number_input("Angsuran/Month (Rp)", 0)
        crew = st.sidebar.number_input("Crew cost/Month (Rp)", 0)
        insurance = st.sidebar.number_input("Insurance/Month (Rp)", 0)
        docking = st.sidebar.number_input("Docking-Saving/Month (Rp)", 0)
        maintenance = st.sidebar.number_input("Maintenance/Month (Rp)", 0)
    else:
        charter = st.sidebar.number_input("Charter hire/Month (Rp)", 0)
        crew = insurance = docking = maintenance = 0

    port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", 0)
    port_stay_pol = st.sidebar.number_input("Port Stay POL (Day)", 0)
    port_stay_pod = st.sidebar.number_input("Port Stay POD (Day)", 0)

    # ===== INPUT UTAMA =====
    col1, col2 = st.columns(2)
    with col1:
        pol = st.text_input("Port of Loading (POL)")
        type_cargo = st.selectbox("Type Cargo", ["Pasir (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"])
        distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0)
    with col2:
        pod = st.text_input("Port of Discharge (POD)")
        qyt_cargo = st.number_input("QYT Cargo", 0.0)
        distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0)

    # ===== PERHITUNGAN =====
    if st.button("Hitung Freight Cost"):
        try:
            sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
            total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
            total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)

            charter_cost = (charter / 30) * total_voyage_days
            bunker_cost = total_consumption * price_bunker
            port_cost = port_cost_pol + port_cost_pod
            premi_cost = distance_pol_pod * premi_nm
            crew_cost = (crew / 30) * total_voyage_days
            insurance_cost = (insurance / 30) * total_voyage_days
            docking_cost = (docking / 30) * total_voyage_days
            maintenance_cost = (maintenance / 30) * total_voyage_days

            total_cost = (
                charter_cost + bunker_cost + port_cost + premi_cost + crew_cost +
                asist_tug + insurance_cost + docking_cost + maintenance_cost + other_cost
            )

            freight_cost_mt = total_cost / qyt_cargo if qyt_cargo > 0 else 0

            # ===== TAMPILKAN HASIL =====
            st.subheader("📋 Hasil Perhitungan")
            st.write(f"**POL → POD**: {pol} → {pod}")
            st.write(f"**Sailing Time (Hour)**: {sailing_time:,.2f}")
            st.write(f"**Total Voyage Days**: {total_voyage_days:,.2f}")
            st.write(f"**Total Consumption (liter)**: {total_consumption:,.2f}")
            st.write(f"**Total Cost (Rp)**: {total_cost:,.2f}")
            st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]})**: {freight_cost_mt:,.2f}")

            # ===== TABEL PROFIT =====
            data = []
            for p in range(0, 55, 5):
                freight_persen = freight_cost_mt * (1 + p / 100)
                revenue = freight_persen * qyt_cargo
                pph = revenue * 0.012
                profit = revenue - total_cost - pph
                data.append([f"{p}%", f"{freight_persen:,.2f}", f"{revenue:,.2f}", f"{pph:,.2f}", f"{profit:,.2f}"])

            df_profit = pd.DataFrame(data, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
            st.dataframe(df_profit)

            # ===== PDF GENERATOR =====
            def create_pdf():
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []

                elements.append(Paragraph("<b>Freight Calculator Barge</b>", styles['Title']))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Mode: {mode}", styles['Normal']))
                elements.append(Paragraph(f"User: {st.session_state['user']}", styles['Normal']))
                elements.append(Spacer(1, 12))

                params = [
                    ["Speed Laden", f"{speed_laden} knot"],
                    ["Speed Ballast", f"{speed_ballast} knot"],
                    ["Consumption", f"{consumption} L/h"],
                    ["Price Bunker", f"Rp {price_bunker:,.0f}"],
                    ["Distance POL-POD", f"{distance_pol_pod} NM"],
                    ["Distance POD-POL", f"{distance_pod_pol} NM"],
                    ["QYT Cargo", f"{qyt_cargo} {type_cargo.split()[1]}"]
                ]
                t = Table(params, hAlign='LEFT')
                t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
                elements.append(t)
                elements.append(Spacer(1, 12))

                hasil = [
                    ["Sailing Time (Hour)", f"{sailing_time:,.2f}"],
                    ["Total Voyage Days", f"{total_voyage_days:,.2f}"],
                    ["Total Cost (Rp)", f"{total_cost:,.2f}"],
                    ["Freight Cost", f"{freight_cost_mt:,.2f}"]
                ]
                t2 = Table(hasil, hAlign='LEFT')
                t2.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
                elements.append(t2)
                elements.append(Spacer(1, 12))

                profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
                t3 = Table(profit_table, hAlign='LEFT')
                t3.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black),
                                        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)]))
                elements.append(t3)
                elements.append(Spacer(1, 18))

                elements.append(Paragraph("<i>Generated by Freight Calculator APP Iqna</i>", styles['Normal']))
                doc.build(elements)
                buffer.seek(0)
                return buffer

            pdf_buffer = create_pdf()
            st.download_button("📥 Download PDF", data=pdf_buffer, file_name="Freight_Calculator_Barge.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# ========== MAIN FLOW ==========
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" in st.session_state:
    main_app()
elif st.session_state.page == "register":
    register_page()
else:
    login_page()
