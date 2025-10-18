import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import tempfile
import math

# ===== FIREBASE SETUP =====
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # file key Firebase kamu
    firebase_admin.initialize_app(cred)

# ===== SESSION =====
if "user" not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.user = None
    st.experimental_rerun()

# ===== LOGIN PAGE =====
def login_page():
    st.title("🚢 Freight Calculator Login")
    st.write("Masuk menggunakan akun Firebase kamu")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.get_user_by_email(email)
            st.session_state.user = email
            st.success("Login berhasil ✅")
            st.experimental_rerun()
        except Exception as e:
            st.error("Login gagal. Pastikan email terdaftar.")

    st.write("---")
    st.write("Belum punya akun?")
    if st.button("Daftar"):
        register_page()

# ===== REGISTER PAGE =====
def register_page():
    st.title("📝 Daftar Akun Baru")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_pass")

    if st.button("Buat Akun"):
        try:
            auth.create_user(email=email, password=password)
            st.success("Akun berhasil dibuat! Silakan login.")
            st.experimental_rerun()
        except Exception:
            st.error("Gagal membuat akun. Mungkin email sudah digunakan.")

# ===== PDF EXPORT =====
def export_pdf(data):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "🚢 Freight Profit Calculation Report")
    c.setFont("Helvetica", 11)

    y = height - 100
    for key, val in data.items():
        c.drawString(80, y, f"{key}: {val}")
        y -= 20

    c.save()
    return tmp.name

# ===== MAIN APP =====
def main_app():
    st.title("⚓ Freight Cost & Profit Dashboard")
    st.markdown("Hitung biaya operasi kapal dan estimasi profit dengan cepat dan mudah 💼")

    # ===== SIDEBAR =====
    st.sidebar.markdown("<h2 style='text-align:center;'>⚙️ Parameter Input</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    mode = st.sidebar.radio("Mode Operasi", ["Owner", "Charter"])
    st.sidebar.markdown("### ⚓ Voyage Parameter")
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0)
    distance_pol_pod = st.sidebar.number_input("Distance POL - POD (NM)", 0.0)
    distance_pod_pol = st.sidebar.number_input("Distance POD - POL (NM)", 0.0)

    st.sidebar.markdown("### ⛽ Fuel & Bunker")
    consumption = st.sidebar.number_input("Consumption Fuel (liter/jam)", 0)
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0)
    premi_nm = st.sidebar.number_input("Premi (Rp/NM)", 0)

    st.sidebar.markdown("### ⚓ Port Cost")
    port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", 0)
    other_cost = st.sidebar.number_input("Other Cost (Rp)", 0)
    port_stay_pol = st.sidebar.number_input("Port Stay POL (Hari)", 0)
    port_stay_pod = st.sidebar.number_input("Port Stay POD (Hari)", 0)

    # ===== MODE PARAMETER =====
    if mode == "Owner":
        st.sidebar.markdown("### 🧾 Fixed Cost (Owner Mode)")
        charter = st.sidebar.number_input("Angsuran/Month (Rp)", 0)
        crew = st.sidebar.number_input("Crew cost/Month (Rp)", 0)
        insurance = st.sidebar.number_input("Insurance/Month (Rp)", 0)
        docking = st.sidebar.number_input("Docking-Saving/Month (Rp)", 0)
        maintenance = st.sidebar.number_input("Maintenance/Month (Rp)", 0)
    else:
        st.sidebar.markdown("### 🧾 Fixed Cost (Charter Mode)")
        charter = st.sidebar.number_input("Charter hire/Month (Rp)", 0)
        crew = insurance = docking = maintenance = 0

    st.sidebar.markdown("---")
    st.sidebar.button("Logout", on_click=logout)

    # ===== CALCULATION =====
    sea_time_laden = distance_pol_pod / (speed_laden * 24) if speed_laden > 0 else 0
    sea_time_ballast = distance_pod_pol / (speed_ballast * 24) if speed_ballast > 0 else 0
    total_port_stay = port_stay_pol + port_stay_pod
    total_day = sea_time_laden + sea_time_ballast + total_port_stay

    fuel_cost = (sea_time_laden + sea_time_ballast) * 24 * consumption * price_bunker
    premi_cost = (distance_pol_pod + distance_pod_pol) * premi_nm
    port_cost_total = port_cost_pol + port_cost_pod + asist_tug + other_cost
    fix_cost_monthly = charter + crew + insurance + docking + maintenance
    fix_cost_voy = fix_cost_monthly * (total_day / 30)
    total_cost = fuel_cost + premi_cost + port_cost_total + fix_cost_voy

    revenue = st.number_input("Revenue (Rp)", 0)
    pph = 0.025 * revenue
    profit = revenue - total_cost - pph

    # ===== OUTPUT DASHBOARD =====
    st.markdown("## 📊 Hasil Perhitungan")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Voyage (Hari)", f"{total_day:.2f}")
        st.metric("Fuel Cost", f"Rp {fuel_cost:,.0f}")
        st.metric("Premi", f"Rp {premi_cost:,.0f}")

    with col2:
        st.metric("Port Cost", f"Rp {port_cost_total:,.0f}")
        st.metric("Fixed Cost (Prorata)", f"Rp {fix_cost_voy:,.0f}")
        st.metric("Total Cost", f"Rp {total_cost:,.0f}")

    with col3:
        st.metric("Revenue", f"Rp {revenue:,.0f}")
        st.metric("PPh 2.5%", f"Rp {pph:,.0f}")
        st.metric("💰 Profit", f"Rp {profit:,.0f}")

    # ===== PDF EXPORT =====
    data = {
        "Mode": mode,
        "Total Hari Voyage": f"{total_day:.2f}",
        "Fuel Cost": f"Rp {fuel_cost:,.0f}",
        "Premi": f"Rp {premi_cost:,.0f}",
        "Port Cost": f"Rp {port_cost_total:,.0f}",
        "Fixed Cost (Prorata)": f"Rp {fix_cost_voy:,.0f}",
        "Total Cost": f"Rp {total_cost:,.0f}",
        "Revenue": f"Rp {revenue:,.0f}",
        "PPh 2.5%": f"Rp {pph:,.0f}",
        "Profit": f"Rp {profit:,.0f}",
    }

    if st.button("📄 Download PDF Report"):
        pdf_path = export_pdf(data)
        with open(pdf_path, "rb") as f:
            st.download_button("Download Sekarang", f, file_name="Freight_Report.pdf")

# ===== MAIN CONTROL =====
if st.session_state.user is None:
    login_page()
else:
    main_app()
