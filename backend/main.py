import streamlit as st
import pandas as pd
import hashlib

# ======= CONFIGURASI DASAR =======
st.set_page_config(page_title="Freight Calculator Demo", layout="wide")

# ======= SIMULASI DATABASE USER (PAKE CSV) =======
USER_DB = "users.csv"

# Buat file users.csv kalau belum ada
try:
    users = pd.read_csv(USER_DB)
except FileNotFoundError:
    users = pd.DataFrame(columns=["username", "password"])
    users.to_csv(USER_DB, index=False)

# ======= FUNGSI HASH PASSWORD =======
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======= FUNGSI CEK LOGIN =======
def check_login(username, password):
    users = pd.read_csv(USER_DB)
    hashed = hash_password(password)
    return ((users["username"] == username) & (users["password"] == hashed)).any()

# ======= FUNGSI DAFTAR USER BARU =======
def register_user(username, password):
    users = pd.read_csv(USER_DB)
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_DB, index=False)
    return True

# ======= HALAMAN LOGIN =======
def login_page():
    st.title("🔐 Login ke Freight Calculator")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if check_login(username, password):
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.experimental_rerun()
        else:
            st.error("Username atau password salah!")

    st.markdown("---")
    if st.button("Daftar di sini"):
        st.session_state["show_register"] = True
        st.experimental_rerun()

# ======= HALAMAN REGISTER =======
def register_page():
    st.title("📝 Daftar Akun Baru")

    username = st.text_input("Buat Username")
    password = st.text_input("Buat Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")

    if st.button("Daftar"):
        if password != confirm:
            st.warning("Password tidak cocok!")
        elif username == "" or password == "":
            st.warning("Isi semua kolom dulu bro!")
        elif register_user(username, password):
            st.success("Berhasil daftar! Silakan login.")
            st.session_state["show_register"] = False
        else:
            st.error("Username sudah terdaftar!")

    if st.button("Kembali ke Login"):
        st.session_state["show_register"] = False
        st.experimental_rerun()

# ======= HALAMAN UTAMA (SETELAH LOGIN) =======
def main_app():
    st.title("🚢 Freight Calculator")
    st.sidebar.success(f"Login sebagai: {st.session_state['user']}")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()

    # ======= CONTOH FITUR KALKULATOR FREIGHT =======
    st.subheader("Hitung Freight Cost")
    col1, col2, col3 = st.columns(3)
    with col1:
        distance = st.number_input("Jarak (mil laut)", min_value=0.0)
    with col2:
        rate = st.number_input("Tarif per mil laut ($)", min_value=0.0)
    with col3:
        surcharge = st.number_input("Surcharge (%)", min_value=0.0, max_value=100.0)

    if st.button("Hitung"):
        total = distance * rate * (1 + surcharge / 100)
        st.success(f"💰 Total Freight Cost: ${total:,.2f}")

# ======= SISTEM HALAMAN DINAMIS =======
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    if st.session_state["show_register"]:
        register_page()
    else:
        login_page()
