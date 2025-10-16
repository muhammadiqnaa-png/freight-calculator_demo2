# app.py
import streamlit as st
import requests
import pandas as pd
import hashlib
import os

st.set_page_config(page_title="Freight Calculator (Firebase Auth)", layout="wide")

# --------------------------
# FIREBASE REST endpoints
# --------------------------
API_KEY = st.secrets.get("FIREBASE_API_KEY", None)
if not API_KEY:
    st.error("FIREBASE_API_KEY belum diset di Streamlit Secrets. Stop.")
    st.stop()

FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
FIREBASE_LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

# --------------------------
# Helper: hash (optional local)
# --------------------------
def short_hash(s):
    return hashlib.sha1(s.encode()).hexdigest()[:8]

# --------------------------
# Session defaults
# --------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "idToken" not in st.session_state:
    st.session_state.idToken = None

# --------------------------
# UI: Login / Register
# --------------------------
def show_auth_forms():
    st.title("🔐 Login / Daftar — Freight Calculator")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Daftar Baru"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            if not email or not password:
                st.error("Isi email & password.")
            else:
                try:
                    payload = {"email": email, "password": password, "returnSecureToken": True}
                    r = requests.post(FIREBASE_LOGIN_URL, json=payload, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state.user = data.get("email")
                        st.session_state.idToken = data.get("idToken")
                        st.success("Login berhasil ✅")
                        st.experimental_rerun()
                    else:
                        # extract message if available
                        err = r.json().get("error", {}).get("message", r.text)
                        st.error(f"Login gagal: {err}")
                except Exception as e:
                    st.error(f"Gagal terhubung ke Firebase: {e}")

    with tab2:
        email_r = st.text_input("Email", key="reg_email")
        pw_r = st.text_input("Password", type="password", key="reg_pw")
        pw_r2 = st.text_input("Konfirmasi Password", type="password", key="reg_pw2")
        if st.button("Daftar"):
            if not email_r or not pw_r:
                st.warning("Isi semua kolom dulu.")
            elif pw_r != pw_r2:
                st.warning("Password tidak cocok.")
            else:
                try:
                    payload = {"email": email_r, "password": pw_r, "returnSecureToken": True}
                    r = requests.post(FIREBASE_SIGNUP_URL, json=payload, timeout=10)
                    if r.status_code == 200:
                        st.success("Registrasi berhasil! Silakan login.")
                    else:
                        err = r.json().get("error", {}).get("message", r.text)
                        st.error(f"Gagal registrasi: {err}")
                except Exception as e:
                    st.error(f"Gagal terhubung ke Firebase: {e}")

# --------------------------
# Main freight app (after login)
# --------------------------
def main_app():
    st.sidebar.success(f"Login sebagai: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.idToken = None
        st.experimental_rerun()

    st.title("🚢 Freight Calculator")
    st.write("Masukkan parameter untuk menghitung biaya freight:")

    origin = st.text_input("Asal Pelabuhan")
    destination = st.text_input("Tujuan Pelabuhan")
    total_cargo = st.number_input("Total Cargo (MT)", value=7500.0)
    jarak = st.number_input("Jarak (NM)", value=630.0)

    # contoh parameter default
    speed_kosong = st.number_input("Speed Kosong (knot)", value=3.0)
    speed_isi = st.number_input("Speed Isi (knot)", value=4.0)
    consumption = st.number_input("Consumption (liter/jam)", value=120.0)
    harga_bunker = st.number_input("Harga Bunker (Rp/liter)", value=12500.0)
    port_stay = st.number_input("Port Stay (Hari)", value=10)

    if st.button("Hitung Freight"):
        sailing_time = (jarak / speed_kosong) + (jarak / speed_isi)
        voyage_days = (sailing_time / 24) + port_stay
        total_consumption = (sailing_time * consumption) + (port_stay * consumption)
        biaya_bunker = total_consumption * harga_bunker
        # contoh simple total cost
        total_cost = biaya_bunker
        cost_per_mt = total_cost / total_cargo if total_cargo else 0

        st.write(f"Sailing Time (jam): {sailing_time:,.2f}")
        st.write(f"Total Voyage Days: {voyage_days:,.2f}")
        st.write(f"Total Consumption (liter): {total_consumption:,.0f}")
        st.write(f"TOTAL COST: Rp {total_cost:,.0f}")
        st.write(f"FREIGHT: Rp {cost_per_mt:,.0f} / MT")

# --------------------------
# App entry
# --------------------------
if st.session_state.user:
    main_app()
else:
    show_auth_forms()
