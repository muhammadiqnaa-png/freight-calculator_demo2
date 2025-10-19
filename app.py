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

# ===== LOGOUT =====
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"Logged in as: **{st.session_state.email}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.success("Successfully logged out.")
    st.rerun()

# ===== MODE =====
mode = st.sidebar.selectbox("Mode", ["Owner", "Charter"])

# ===== SIDEBAR PARAMETERS =====
with st.sidebar.expander("🚢 Speed"):
    speed_laden = st.number_input("Speed Laden (knot)", 0.0)
    speed_ballast = st.number_input("Speed Ballast (knot)", 0.0)

with st.sidebar.expander("⛽ Fuel"):
    consumption = st.number_input("Consumption Fuel (liter/hour)", 0)
    price_fuel = st.number_input("Price Fuel (Rp/Ltr)", 0)

with st.sidebar.expander("💧 Freshwater"):
    consumption_fw = st.number_input("Consumption Freshwater (Ton/Day)", 0)
    price_fw = st.number_input("Price Freshwater (Rp/Ton)", 0)

if mode == "Owner":
    with st.sidebar.expander("🏗️ Owner Cost"):
        charter = st.number_input("Angsuran (Rp/Month)", 0)
        crew = st.number_input("Crew (Rp/Month)", 0)
        insurance = st.number_input("Insurance (Rp/Month)", 0)
        docking = st.number_input("Docking (Rp/Month)", 0)
        maintenance = st.number_input("Maintenance (Rp/Month)", 0)
        certificate = st.number_input("Certificate (Rp/Month)", 0)
        premi_nm = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)
else:
    with st.sidebar.expander("🏗️ Charter Cost"):
        charter = st.number_input("Charter Hire (Rp/Month)", 0)
        premi_nm = st.number_input("Premi (Rp/NM)", 0)
        other_cost = st.number_input("Other Cost (Rp)", 0)

with st.sidebar.expander("⚓ Port Cost"):
    port_cost_pol = st.number_input("Port Cost POL (Rp)", 0)
    port_cost_pod = st.number_input("Port Cost POD (Rp)", 0)
    asist_tug = st.number_input("Asist Tug (Rp)", 0)

with st.sidebar.expander("🕓 Port Stay"):
    port_stay_pol = st.number_input("POL (Days)", 0)
    port_stay_pod = st.number_input("POD (Days)", 0)

# ===== MAIN INPUT =====
st.title("🚢 Freight Calculator Barge")

col1, col2, col3 = st.columns(3)
with col1:
    port_pol = st.text_input("Port Of Loading")
with col2:
    port_pod = st.text_input("Port Of Discharge")
with col3:
    next_port = st.text_input("Next Port")

type_cargo = st.selectbox("Type Cargo", ["Bauxite (M3)", "Sand (M3)", "Coal (MT)", "Nickel (MT)", "Split (M3)"])
qyt_cargo = st.number_input("Cargo Quantity", 0.0)
distance_pol_pod = st.number_input("Distance POL - POD (NM)", 0.0)
distance_pod_pol = st.number_input("Distance POD - POL (NM)", 0.0)

# ===== PERHITUNGAN =====
if st.button("Calculate Freight 💸"):
    try:
        # Sailing Time
        sailing_time = (distance_pol_pod / speed_laden) + (distance_pod_pol / speed_ballast)
        total_voyage_days = (sailing_time / 24) + (port_stay_pol + port_stay_pod)
        total_voyage_days_round = int(total_voyage_days) if total_voyage_days %1 <0.5 else int(total_voyage_days)+1

        # Fuel & Freshwater
        total_consumption_fuel = (sailing_time * consumption) + ((port_stay_pol + port_stay_pod) * 120)
        total_consumption_fw = consumption_fw * total_voyage_days_round
        cost_fw = total_consumption_fw * price_fw
        cost_fuel = total_consumption_fuel * price_fuel

        # Costs
        charter_cost = (charter / 30) * total_voyage_days if mode=="Owner" else (charter / 30) * total_voyage_days
        crew_cost = (crew /30) * total_voyage_days if mode=="Owner" else 0
        insurance_cost = (insurance /30)* total_voyage_days if mode=="Owner" else 0
        docking_cost = (docking /30)* total_voyage_days if mode=="Owner" else 0
        maintenance_cost = (maintenance /30)* total_voyage_days if mode=="Owner" else 0
        certificate_cost = (certificate /30)* total_voyage_days if mode=="Owner" else 0
        premi_cost = distance_pol_pod * premi_nm
        port_cost = port_cost_pol + port_cost_pod + asist_tug

        total_cost = sum([
            charter_cost, crew_cost, insurance_cost, docking_cost, maintenance_cost, certificate_cost,
            premi_cost, port_cost, cost_fuel, cost_fw, other_cost
        ])

        freight_cost_mt = total_cost / qyt_cargo if qyt_cargo>0 else 0

        # ===== DISPLAY RESULTS =====
        st.subheader("📋 Calculation Results")
        st.markdown(f"""
**Port Of Loading:** {port_pol}  
**Port Of Discharge:** {port_pod}  
**Next Port:** {next_port}  
**Type Cargo:** {type_cargo}  
**Cargo Quantity:** {qyt_cargo:,.0f} {type_cargo.split()[1]}  
**Distance (NM):** {distance_pol_pod:,.0f}  
**Total Voyage (Days):** {total_voyage_days:.2f}  
**Total Sailing Time (Hour):** {sailing_time:.2f}  
**Total Consumption Fuel (Ltr):** {total_consumption_fuel:,.0f}  
**Total Consumption Freshwater (Ton):** {total_consumption_fw:,.0f}  
**Fuel Cost (Rp):** Rp {cost_fuel:,.0f}  
**Freshwater Cost (Rp):** Rp {cost_fw:,.0f}  
""")

        if mode=="Owner":
            st.markdown(f"""
**Owner Costs (Rp):**  
- Charter: Rp {charter_cost:,.0f}  
- Crew: Rp {crew_cost:,.0f}  
- Insurance: Rp {insurance_cost:,.0f}  
- Docking: Rp {docking_cost:,.0f}  
- Maintenance: Rp {maintenance_cost:,.0f}  
- Certificate: Rp {certificate_cost:,.0f}  
- Premi: Rp {premi_cost:,.0f}  
- Port Costs: Rp {port_cost:,.0f}  
- Other Costs: Rp {other_cost:,.0f}  
**🧮Total Cost:** Rp {total_cost:,.0f}  
**🧮Freight Cost ({type_cargo.split()[1]}):** Rp {freight_cost_mt:,.0f}
""")
        else:
            st.markdown(f"""
**Charter Costs (Rp):**  
- Charter Hire: Rp {charter_cost:,.0f}  
- Premi: Rp {premi_cost:,.0f}  
- Port Costs: Rp {port_cost:,.0f}  
- Other Costs: Rp {other_cost:,.0f}  
**🧮Total Cost:** Rp {total_cost:,.0f}  
**🧮Freight Cost ({type_cargo.split()[1]}):** Rp {freight_cost_mt:,.0f}
""")

        # ===== PROFIT SCENARIO =====
        data = []
        for p in range(0,55,5):
            freight_persen = freight_cost_mt*(1+p/100)
            revenue = freight_persen*qyt_cargo
            pph = revenue*0.012
            profit = revenue - total_cost - pph
            data.append([f"{p}%", f"Rp {freight_persen:,.0f}", f"Rp {revenue:,.0f}", f"Rp {pph:,.0f}", f"Rp {profit:,.0f}"])
        df_profit = pd.DataFrame(data, columns=["Profit %","Freight (Rp)","Revenue (Rp)","PPH 1.2% (Rp)","Profit (Rp)"])
        st.subheader("💰 Profit Scenario 0-50%")
        st.dataframe(df_profit, use_container_width=True)

        # ===== PDF GENERATOR =====
        def create_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20,leftMargin=20,topMargin=20,bottomMargin=20)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            elements.append(Paragraph("<b>Freight Calculator Report</b>", styles['Title']))
            elements.append(Spacer(1,12))

            # Voyage Information
            elements.append(Paragraph("<b>Voyage Information</b>", styles['Heading3']))
            voyage_data = [
                ["Port Of Loading", port_pol],
                ["Port Of Discharge", port_pod],
                ["Next Port", next_port],
                ["Cargo Quantity", f"{qyt_cargo:,.0f} {type_cargo.split()[1]}"],
                ["Distance (NM)", f"{distance_pol_pod:,.0f}"],
                ["Total Voyage (Days)", f"{total_voyage_days:.2f}"]
            ]
            t_voyage = Table(voyage_data, hAlign='LEFT')
            t_voyage.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
            elements.append(t_voyage)
            elements.append(Spacer(1,12))

            # Calculation Results
            elements.append(Paragraph("<b>Calculation Results</b>", styles['Heading3']))
            calc_data = [
                ["Total Sailing Time (Hour)", f"{sailing_time:.2f}"],
                ["Total Consumption Fuel (Ltr)", f"Rp {total_consumption_fuel:,.0f}"],
                ["Total Consumption Freshwater (Ton)", f"Rp {total_consumption_fw:,.0f}"],
                ["Fuel Cost (Rp)", f"Rp {cost_fuel:,.0f}"],
                ["Freshwater Cost (Rp)", f"Rp {cost_fw:,.0f}"]
            ]
            if mode=="Owner":
                calc_data += [
                    ["Charter (Rp)", f"Rp {charter_cost:,.0f}"],
                    ["Crew (Rp)", f"Rp {crew_cost:,.0f}"],
                    ["Insurance (Rp)", f"Rp {insurance_cost:,.0f}"],
                    ["Docking (Rp)", f"Rp {docking_cost:,.0f}"],
                    ["Maintenance (Rp)", f"Rp {maintenance_cost:,.0f}"],
                    ["Certificate (Rp)", f"Rp {certificate_cost:,.0f}"],
                    ["Premi (Rp)", f"Rp {premi_cost:,.0f}"],
                    ["Port Costs (Rp)", f"Rp {port_cost:,.0f}"],
                    ["Other Costs (Rp)", f"Rp {other_cost:,.0f}"],
                    ["Total Cost (Rp)", f"Rp {total_cost:,.0f}"],
                    [f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"]
                ]
            else:
                calc_data += [
                    ["Charter Hire (Rp)", f"Rp {charter_cost:,.0f}"],
                    ["Premi (Rp)", f"Rp {premi_cost:,.0f}"],
                    ["Port Costs (Rp)", f"Rp {port_cost:,.0f}"],
                    ["Other Costs (Rp)", f"Rp {other_cost:,.0f}"],
                    ["Total Cost (Rp)", f"Rp {total_cost:,.0f}"],
                    [f"Freight Cost ({type_cargo.split()[1]})", f"Rp {freight_cost_mt:,.0f}"]
                ]
            t_calc = Table(calc_data, hAlign='LEFT', colWidths=[180,120])
            t_calc.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
            elements.append(t_calc)
            elements.append(Spacer(1,12))

            # Profit Scenario
            elements.append(Paragraph("<b>Profit Scenario 0-50%</b>", styles['Heading3']))
            profit_table = [df_profit.columns.to_list()] + df_profit.values.tolist()
            t_profit = Table(profit_table, hAlign='LEFT', colWidths=[60,100,100,100,100])
            t_profit.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.black)]))
            elements.append(t_profit)
            elements.append(Spacer(1,12))

            # Footer
            elements.append(Paragraph("<i>Generated By: https://freight-calculatordemo2.streamlit.app/</i>", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf()
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="Freight_Calculator_Report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")

