import streamlit as st
import pandas as pd
import hashlib

# ====== KONFIGURASI ======
st.set_page_config(page_title="Freight Calculator Demo", layout="wide")
USER_DB = "users.csv"

# ====== FUNGSI PASSWORD HASH ======
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ====== LOAD / INIT USER DB ======
try:
    users = pd.read_csv(USER_DB)
except FileNotFoundError:
    users = pd.DataFrame(columns=["email", "password"])
    users.to_csv(USER_DB, index=False)

# ====== REGISTER USER ======
def register_user(email, password):
    users = pd.read_csv(USER_DB)
    if email in users["email"].values:
        return False
    new_user = pd.DataFrame([[email, hash_password(password)]], columns=["email", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_DB, index=False)
    return True

# ====== CHECK LOGIN ======
def check_login(email, password):
    users = pd.read_csv(USER_DB)
    hashed = hash_password(password)
    return ((users["email"] == email) & (users["password"] == hashed)).any()

# ====== STATE ======
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""

# ====== LOGIN / REGISTER ======
if not st.session_state.logged_in:
    st.title("🔐 Login / Daftar — Freight Calculator Demo")
    tab1, tab2 = st.tabs(["Login", "Daftar Baru"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_login(email, password):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("✅ Login berhasil!")
                st.rerun()
            else:
                st.error("❌ Email atau password salah!")

    with tab2:
        email_r = st.text_input("Email", key="reg_email")
        pw_r = st.text_input("Password", type="password", key="reg_pw")
        pw_r2 = st.text_input("Konfirmasi Password", type="password", key="reg_pw2")
        if st.button("Daftar"):
            if not email_r or not pw_r:
                st.warning("Isi semua kolom bro!")
            elif pw_r != pw_r2:
                st.warning("Password tidak cocok!")
            elif register_user(email_r, pw_r):
                st.success("✅ Registrasi berhasil! Silakan login.")
            else:
                st.error("❌ Email sudah terdaftar.")

    st.stop()

# ====== HALAMAN UTAMA ======
st.sidebar.success(f"👋 Selamat datang, {st.session_state.email}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.rerun()

st.title("🚢 Freight Calculator Demo")

origin = st.text_input("Asal Pelabuhan")
destination = st.text_input("Tujuan Pelabuhan")
weight = st.number_input("Berat (kg)", min_value=0.0, step=0.1)

if st.button("Hitung Freight"):
    if not origin or not destination or weight <= 0:
        st.warning("Isi semua field dengan benar.")
    else:
        freight_cost = weight * 0.75  # contoh rumus sederhana
        st.success(f"💰 Total biaya freight: ${freight_cost:,.2f}")
