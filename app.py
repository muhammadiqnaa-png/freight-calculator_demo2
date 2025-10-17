import streamlit as st
import requests
import pandas as pd

# ====== KONFIGURASI DASAR ======
st.set_page_config(page_title="Freight Calculator Demo", layout="wide")

# Ganti URL backend kamu di sini
BACKEND = st.secrets.get("backend_url", "https://freight-demo.streamlit.app/backend")

# ====== STATE AWAL ======
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.username = ""

# ====== HALAMAN LOGIN / DAFTAR ======
if not st.session_state.logged_in:
    st.title("🔐 Login / Daftar — Freight Calculator Demo")

    tab1, tab2 = st.tabs(["Login", "Daftar Baru"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("Login"):
            try:
                r = requests.post(f"{BACKEND}/login", json={"email": email, "password": password}, timeout=10)
                if r.status_code == 200 and "status" in r.json():
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.username = email.split("@")[0]
                    st.success("✅ Login berhasil, membuka aplikasi...")
                    st.rerun()
                else:
                    st.error("❌ Email atau password salah")
            except Exception as e:
                st.error(f"Gagal terhubung ke backend: {e}")

    with tab2:
        email_r = st.text_input("Email", key="reg_email")
        password_r = st.text_input("Password", type="password", key="reg_pw")
        password_r2 = st.text_input("Konfirmasi Password", type="password", key="reg_pw2")

        if st.button("Daftar"):
            if not email_r or not password_r:
                st.error("Email & password wajib diisi")
            elif password_r != password_r2:
                st.error("Konfirmasi password tidak cocok")
            else:
                try:
                    r = requests.post(f"{BACKEND}/register", json={"email": email_r, "password": password_r}, timeout=10)
                    if r.status_code == 200 and "status" in r.json():
                        st.success("✅ Registrasi berhasil, silakan login")
                    else:
                        st.error("❌ Gagal registrasi (email mungkin sudah terdaftar)")
                except Exception as e:
                    st.error(f"Gagal terhubung ke backend: {e}")

    st.stop()

# ====== HALAMAN UTAMA ======
st.sidebar.success(f"👋 Selamat datang, {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.username = ""
    st.rerun()

st.title("🚢 Freight Calculator Demo")

st.write("Masukkan parameter untuk menghitung biaya freight:")

origin = st.text_input("Asal Pelabuhan")
destination = st.text_input("Tujuan Pelabuhan")
weight = st.number_input("Berat (kg)", min_value=0.0, step=0.1)

if st.button("Hitung"):
    if not origin or not destination or weight <= 0:
        st.warning("Mohon isi semua field dengan benar.")
    else:
        try:
            response = requests.post(f"{BACKEND}/calculate", json={
                "origin": origin,
                "destination": destination,
                "weight": weight
            }, timeout=10)

            if response.status_code == 200:
                result = response.json()
                st.success(f"💰 Total biaya freight: ${result['freight_cost']}")
            else:
                st.error("Gagal menghitung biaya freight.")
        except Exception as e:
            st.error(f"Gagal hubungi backend: {e}")
