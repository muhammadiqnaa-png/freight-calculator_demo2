# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# import halaman auth (pastikan folder auth/ punya login.py & register.py)
try:
    from auth.login import login_page
    from auth.register import register_page
except Exception as e:
    # Jika import gagal, kita buat fallback sederhana agar developer tahu
    def login_page():
        st.error("auth.login tidak ditemukan. Pastikan auth/login.py tersedia.")

    def register_page():
        st.error("auth.register tidak ditemukan. Pastikan auth/register.py tersedia.")

# ---------- page config ----------
st.set_page_config(page_title="Freight Calculator Barge", layout="wide")

# ---------- session init ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# ---------- AUTH FLOW ----------
if not st.session_state.authenticated:
    # tampilkan login/register dari auth module
    st.sidebar.title("🔐 Masuk / Daftar")
    menu = st.sidebar.radio("Pilih", ["Login", "Register"])
    if menu == "Login":
        login_page()
    else:
        register_page()

    st.stop()  # stop agar user harus login dulu
# jika sampai sini berarti sudah authenticated

# ---------- MAIN APP ----------
st.sidebar.title("⚙️ Pengaturan")
if st.sidebar.button("Sign out"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.experimental_rerun()

st.title("🚢 Freight Calculator Barge")
st.markdown("Selamat datang — Anda sudah login. Pilih mode dan input parameter di sidebar.")

# ----- Mode selection -----
mode = st.sidebar.radio("Mode Perhitungan", ["Owner", "Charter"])

# ----- Sidebar inputs (dinamis per mode) -----
st.sidebar.markdown("---")
st.sidebar.subheader("⚓ Input Parameter")

# Default port stay values to avoid NameError later
port_stay_pol = 0
port_stay_pod = 0

if mode == "Owner":
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0, format="%.2f")
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0, format="%.2f")
    consumption = st.sidebar.number_input("Consumption Fuel (liter/jam)", 0.0, format="%.2f")
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0.0, format="%.2f")
    angsuran = st.sidebar.number_input("Angsuran/Month (Rp)", 0.0, format="%.2f")
    premi_nm = st.sidebar.number_input("Premi (Rp/NM)", 0.0, format="%.2f")

    crew = st.sidebar.number_input("Crew cost/Month (Rp)", 0.0, format="%.2f")
    insurance = st.sidebar.number_input("Insurance/Month (Rp)", 0.0, format="%.2f")
    docking = st.sidebar.number_input("Docking - Saving/Month (Rp)", 0.0, format="%.2f")
    maintenance = st.sidebar.number_input("Maintenance/Month (Rp)", 0.0, format="%.2f")

    port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", 0.0, format="%.2f")
    port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", 0.0, format="%.2f")
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", 0.0, format="%.2f")
    other_cost = st.sidebar.number_input("Other Cost (Rp)", 0.0, format="%.2f")

    port_stay_pol = st.sidebar.number_input("Port Stay POL (Hari)", 0, step=1)
    port_stay_pod = st.sidebar.number_input("Port Stay POD (Hari)", 0, step=1)

else:  # Charter
    speed_laden = st.sidebar.number_input("Speed Laden (knot)", 0.0, format="%.2f")
    speed_ballast = st.sidebar.number_input("Speed Ballast (knot)", 0.0, format="%.2f")
    consumption = st.sidebar.number_input("Consumption Fuel (liter/jam)", 0.0, format="%.2f")
    price_bunker = st.sidebar.number_input("Price Bunker (Rp/liter)", 0.0, format="%.2f")
    charter = st.sidebar.number_input("Charter Hire/Month (Rp)", 0.0, format="%.2f")
    premi_nm = st.sidebar.number_input("Premi (Rp/NM)", 0.0, format="%.2f")

    port_cost_pol = st.sidebar.number_input("Port Cost POL (Rp)", 0.0, format="%.2f")
    port_cost_pod = st.sidebar.number_input("Port Cost POD (Rp)", 0.0, format="%.2f")
    asist_tug = st.sidebar.number_input("Asist Tug (Rp)", 0.0, format="%.2f")
    other_cost = st.sidebar.number_input("Other Cost (Rp)", 0.0, format="%.2f")

    port_stay_pol = st.sidebar.number_input("Port Stay POL (Hari)", 0, step=1)
    port_stay_pod = st.sidebar.number_input("Port Stay POD (Hari)", 0, step=1)

# ----- Main inputs -----
col1, col2 = st.columns(2)
with col1:
    port_loading = st.text_input("Port of Loading (POL)", "")
with col2:
    port_discharge = st.text_input("Port of Discharge (POD)", "")

type_cargo = st.selectbox("Type Cargo", ["Pasir (M3)", "Split (MT)", "Coal (MT)", "Nickel (MT)"])
qyt_cargo = st.number_input("QYT Cargo", 0.0, format="%.2f")
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0, format="%.2f")
distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0, format="%.2f")

# ----- Calculate -----
if st.button("Hitung Freight Cost"):
    # validations
    if speed_laden <= 0 or speed_ballast <= 0:
        st.error("⚠️ Speed Laden & Speed Ballast harus > 0")
        st.stop()
    if qyt_cargo <= 0:
        st.error("⚠️ QYT Cargo harus > 0")
        st.stop()

    try:
        # Sailing time (hours)
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)

        # Total voyage days & consumption
        # For Owner we include port stay fuel consumption (use 120 L/h as default)
        if mode == "Owner":
            total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
            total_consumption = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        else:
            total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
            total_consumption = (sailing_time * consumption)  # charter: no extra port fuel by default

        bunker_cost = total_consumption * price_bunker
        premi_cost = distance_pol_pod * premi_nm
        port_cost = port_cost_pol + port_cost_pod

        # compute costs per mode
        if mode == "Owner":
            angsuran_cost = (angsuran / 30) * total_voyage_days
            crew_cost = (crew / 30) * total_voyage_days
            insurance_cost = (insurance / 30) * total_voyage_days
            docking_cost = (docking / 30) * total_voyage_days
            maintenance_cost = (maintenance / 30) * total_voyage_days

            total_fixed_cost = angsuran_cost + crew_cost + insurance_cost + docking_cost + maintenance_cost
            total_variable_cost = bunker_cost + port_cost + premi_cost + asist_tug + other_cost
            total_cost = total_fixed_cost + total_variable_cost

        else:  # Charter
            charter_cost = (charter / 30) * total_voyage_days
            total_fixed_cost = charter_cost
            total_variable_cost = bunker_cost + port_cost + premi_cost + asist_tug + other_cost
            total_cost = total_fixed_cost + total_variable_cost

        freight_cost_per_unit = total_cost / qyt_cargo if qyt_cargo > 0 else 0.0

        # ---------- DISPLAY RESULTS ----------
        st.subheader("📋 Hasil Perhitungan Lengkap")
        st.write(f"**Mode**: {mode}")
        st.write(f"**Port Loading**: {port_loading or '-'}")
        st.write(f"**Port Discharge**: {port_discharge or '-'}")
        st.write(f"**Sailing Time (Hour)**: {sailing_time:,.2f}")
        st.write(f"**Total Voyage Days**: {total_voyage_days:,.2f}")
        st.write(f"**Total Consumption (liter)**: {total_consumption:,.2f}")

        # show fixed costs itemized
        st.markdown("#### 🔒 Fixed Cost (itemized)")
        if mode == "Owner":
            st.write(f"Angsuran (Rp/day aprox): Rp {angsuran_cost:,.2f}")
            st.write(f"Crew (Rp/day aprox): Rp {crew_cost:,.2f}")
            st.write(f"Insurance (Rp/day aprox): Rp {insurance_cost:,.2f}")
            st.write(f"Docking (Rp/day aprox): Rp {docking_cost:,.2f}")
            st.write(f"Maintenance (Rp/day aprox): Rp {maintenance_cost:,.2f}")
        else:
            st.write(f"Charter (Rp/day aprox): Rp {charter_cost:,.2f}")

        # variable cost itemized
        st.markdown("#### 🧾 Variable Cost (itemized)")
        st.write(f"Bunker (Rp): Rp {bunker_cost:,.2f}")
        st.write(f"Port Cost POL (Rp): Rp {port_cost_pol:,.2f}")
        st.write(f"Port Cost POD (Rp): Rp {port_cost_pod:,.2f}")
        st.write(f"Premi (Rp): Rp {premi_cost:,.2f}")
        st.write(f"Asist Tug (Rp): Rp {asist_tug:,.2f}")
        st.write(f"Other Cost (Rp): Rp {other_cost:,.2f}")

        st.markdown("#### ➕ Totals")
        st.write(f"**Total Fixed Cost (Rp)**: Rp {total_fixed_cost:,.2f}")
        st.write(f"**Total Variable Cost (Rp)**: Rp {total_variable_cost:,.2f}")
        st.write(f"**Total Cost (Rp)**: Rp {total_cost:,.2f}")
        st.write(f"**Freight Cost (Rp/{type_cargo.split()[1]})**: Rp {freight_cost_per_unit:,.2f}")

        # Profit table
        st.markdown("### 💰 Tabel Profit (Revenue - Total Cost - PPH)")
        profit_rows = []
        for p in range(0, 55, 5):
            freight_with_profit = freight_cost_per_unit * (1 + p / 100)
            revenue = freight_with_profit * qyt_cargo
            pph = revenue * 0.012
            profit = revenue - total_cost - pph
            profit_rows.append([f"{p}%", f"{freight_with_profit:,.2f}", f"{revenue:,.2f}", f"{pph:,.2f}", f"{profit:,.2f}"])

        df_profit = pd.DataFrame(profit_rows, columns=["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"])
        st.dataframe(df_profit, use_container_width=True)

        # ---------- DETAIL COST TABLE ----------
        st.markdown("### 📑 Rincian Biaya")
        if mode == "Owner":
            detail_cost = {
                "Angsuran": angsuran_cost,
                "Crew": crew_cost,
                "Insurance": insurance_cost,
                "Docking": docking_cost,
                "Maintenance": maintenance_cost,
                "Bunker": bunker_cost,
                "Premi": premi_cost,
                "Port POL": port_cost_pol,
                "Port POD": port_cost_pod,
                "Asist Tug": asist_tug,
                "Other": other_cost,
            }
        else:
            detail_cost = {
                "Charter": charter_cost,
                "Bunker": bunker_cost,
                "Premi": premi_cost,
                "Port POL": port_cost_pol,
                "Port POD": port_cost_pod,
                "Asist Tug": asist_tug,
                "Other": other_cost,
            }

        df_detail = pd.DataFrame(list(detail_cost.items()), columns=["Item", "Cost (Rp)"])
        df_detail["Cost (Rp)"] = df_detail["Cost (Rp)"].map(lambda x: f"{x:,.0f}")
        st.dataframe(df_detail, use_container_width=True)

        # ---------- PDF GENERATOR ----------
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("<b>Freight Calculator Barge</b>", styles['Title']))
            elements.append(Spacer(1, 8))
            elements.append(Paragraph(f"<b>Mode:</b> {mode}", styles['Normal']))
            elements.append(Paragraph(f"<b>POL:</b> {port_loading or '-'}", styles['Normal']))
            elements.append(Paragraph(f"<b>POD:</b> {port_discharge or '-'}", styles['Normal']))
            elements.append(Spacer(1, 8))

            elements.append(Paragraph("<b>Parameter Input</b>", styles['Heading3']))
            params = [
                ["Type Cargo", type_cargo],
                ["QYT Cargo", f"{qyt_cargo:,.2f}"],
                ["Distance POL-POD (NM)", f"{distance_pol_pod:,.2f}"],
                ["Distance POD-POL (NM)", f"{distance_pod_pol:,.2f}"],
                ["Speed Laden (knot)", f"{speed_laden:,.2f}"],
                ["Speed Ballast (knot)", f"{speed_ballast:,.2f}"],
                ["Consumption (L/h)", f"{consumption:,.2f}"],
                ["Price Bunker (Rp/L)", f"{price_bunker:,.2f}"],
            ]
            t = Table(params, hAlign='LEFT')
            t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
            elements.append(t)
            elements.append(Spacer(1, 8))

            elements.append(Paragraph("<b>Hasil Perhitungan</b>", styles['Heading3']))
            hasil = [
                ["Sailing Time (Hour)", f"{sailing_time:,.2f}"],
                ["Total Voyage Days", f"{total_voyage_days:,.2f}"],
                ["Total Consumption (liter)", f"{total_consumption:,.2f}"],
                ["Total Fixed Cost (Rp)", f"{total_fixed_cost:,.2f}"],
                ["Total Variable Cost (Rp)", f"{total_variable_cost:,.2f}"],
                ["Total Cost (Rp)", f"{total_cost:,.2f}"],
                [f"Freight Cost (Rp/{type_cargo.split()[1]})", f"{freight_cost_per_unit:,.2f}"],
            ]
            t2 = Table(hasil, hAlign='LEFT')
            t2.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey)]))
            elements.append(t2)
            elements.append(Spacer(1, 8))

            elements.append(Paragraph("<b>Rincian Biaya</b>", styles['Heading3']))
            cost_table = [["Item", "Cost (Rp)"]] + [[k, f"{v:,.0f}"] for k, v in detail_cost.items()]
            t3 = Table(cost_table, hAlign='LEFT')
            t3.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black),
                                     ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)]))
            elements.append(t3)
            elements.append(Spacer(1, 8))

            elements.append(Paragraph("<b>Tabel Profit</b>", styles['Heading3']))
            profit_table = [["Profit %", "Freight (Rp)", "Revenue (Rp)", "PPH 1.2% (Rp)", "Profit (Rp)"]] + profit_rows
            t4 = Table(profit_table, hAlign='LEFT')
            t4.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black),
                                     ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)]))
            elements.append(t4)
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("<i>Generated By Freight Calculator APP Iqna</i>", styles['Normal']))
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()
        st.download_button("📥 Download PDF Hasil", data=pdf_buffer, file_name="Freight_Calculator_Barge.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat perhitungan: {e}")
