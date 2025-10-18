import streamlit as st
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tempfile

# ===== KONFIGURASI FIREBASE =====
API_KEY = st.secrets["FIREBASE_API_KEY"]
FIREBASE_URL_SIGNUP = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
FIREBASE_URL_LOGIN = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

# ===== FUNGSI AUTH =====
def login(email, password):
    res = requests.post(FIREBASE_URL_LOGIN, data={"email": email, "password": password, "returnSecureToken": True})
    return res.json() if res.status_code == 200 else None

def signup(email, password):
    res = requests.post(FIREBASE_URL_SIGNUP, data={"email": email, "password": password, "returnSecureToken": True})
    return res.json() if res.status_code == 200 else None

# ===== LOGIN PAGE =====
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
    if st.button("Daftar Akun Baru"):
        st.session_state.page = "register"
        st.rerun()

# ===== REGISTER PAGE =====
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
            st.error("Gagal daftar. Mungkin email sudah digunakan.")

    if st.button("⬅️ Kembali ke Login"):
        st.session_state.page = "login"
        st.rerun()

# ===== EXPORT PDF =====
def export_pdf(data):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "🚢 Freight Calculator Report")
    c.setFont("Helvetica", 11)
    y = height - 100
    for key, val in data.items():
        c.drawString(80, y, f"{key}: {val}")
        y -= 20
    c.save()
    return tmp.name

# ===== MAIN APP =====
def main_app():
    st.title("⚓ Freight Calculator Barge")
    st.markdown(f"👋 **Logged in as:** {st.session_state.user}")

    with st.sidebar:
        st.markdown("## ⚙️ Input Parameter")
        st.markdown("---")
        mode = st.radio("Mode Operasi", ["Owner", "Charter"])

        st.markdown("### ⚡ Kecepatan & Konsumsi")
        speed_laden = st.number_input("Speed Laden (knot)", 0.0)
        speed_ballast = st.number_input("Speed Ballast (knot)", 0.0)
        consumption = st.number_input("Fuel Consumption (liter/jam)", 0)
        price_bunker = st.number_input("Harga Bunker (Rp/liter)", 0)
        premi_nm = st.number_input("Premi (Rp/NM)", 0)

        st.markdown("---")
        st.markdown("### ⚓ Biaya Pelabuhan & Tambahan")
        port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
        port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
        asist_tug = st.number_input("Asist Tug (Rp)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)
        port_stay_pol = st.number_input("Port Stay POL (Hari)", 0)
        port_stay_pod = st.number_input("Port Stay POD (Hari)", 0)

        st.markdown("---")
        if mode == "Owner":
            st.markdown("### 👷‍♂️ Biaya Operasional (Owner)")
            charter = st.number_input("Angsuran/Month (Rp)", 0)
            crew = st.number_input("Crew/Month (Rp)", 0)
            insurance = st.number_input("Insurance/Month (Rp)", 0)
            docking = st.number_input("Docking-Saving/Month (Rp)", 0)
            maintenance = st.number_input("Maintenance/Month (Rp)", 0)
        else:
            st.markdown("### 🚢 Charter Cost")
            charter = st.number_input("Charter hire/Month (Rp)", 0)
            crew = insurance = docking = maintenance = 0

    # --- Main Content
    st.subheader("📦 Data Voyage")
    distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0)
    distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0)
    qyt_cargo = st.number_input("QTY Cargo", 0.0)
    revenue = st.number_input("Revenue (Rp)", 0)

    if st.button("🚀 Hitung Freight"):
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)

        charter_cost = (charter / 30) * total_voyage_days
        bunker_cost = total_consumption * price_bunker
        premi_cost = distance_pol_pod * premi_nm
        port_cost = port_cost_pol + port_cost_pod
        crew_cost = (crew / 30) * total_voyage_days
        insurance_cost = (insurance / 30) * total_voyage_days
        docking_cost = (docking / 30) * total_voyage_days
        maintenance_cost = (maintenance / 30) * total_voyage_days

        total_cost = (
            charter_cost + bunker_cost + premi_cost + port_cost + asist_tug +
            crew_cost + insurance_cost + docking_cost + maintenance_cost + other_cost
        )

        pph = 0.025 * revenue
        profit = revenue - total_cost - pph

        st.success("✅ Perhitungan selesai!")
        st.markdown("### 📊 Hasil Perhitungan")
        st.write(f"**Total Voyage Days:** {total_voyage_days:,.2f}")
        st.write(f"**Total Cost (Rp):** {total_cost:,.2f}")
        st.write(f"**PPH 2.5% (Rp):** {pph:,.2f}")
        st.write(f"**💰 Profit (Rp):** {profit:,.2f}")

        data = {
            "Mode": mode,
            "Total Voyage Days": f"{total_voyage_days:,.2f}",
            "Total Cost": f"Rp {total_cost:,.2f}",
            "PPH": f"Rp {pph:,.2f}",
            "Profit": f"Rp {profit:,.2f}",
        }

        pdf_path = export_pdf(data)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name="Freight_Report.pdf")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# ===== MAIN CONTROL =====
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    main_app()
elif st.session_state.page == "register":
    register_page()
else:
    login_page()
