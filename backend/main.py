from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd
import hashlib
import os

app = FastAPI()

USER_DB = "users.csv"

# Buat file users.csv kalau belum ada
if not os.path.exists(USER_DB):
    df = pd.DataFrame(columns=["email", "password"])
    df.to_csv(USER_DB, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JSONResponse({"status": "error", "message": "Email dan password wajib diisi"}, status_code=400)

    users = pd.read_csv(USER_DB)
    if email in users["email"].values:
        return JSONResponse({"status": "error", "message": "Email sudah terdaftar"}, status_code=400)

    new_user = pd.DataFrame([[email, hash_password(password)]], columns=["email", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_DB, index=False)

    return {"status": "ok", "message": "User berhasil didaftarkan"}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    users = pd.read_csv(USER_DB)
    hashed = hash_password(password)

    if ((users["email"] == email) & (users["password"] == hashed)).any():
        return {"status": "ok", "message": "Login berhasil"}
    else:
        return JSONResponse({"status": "error", "message": "Email atau password salah"}, status_code=401)

@app.post("/calculate")
async def calculate(request: Request):
    data = await request.json()
    origin = data.get("origin")
    destination = data.get("destination")
    weight = float(data.get("weight", 0))

    if not origin or not destination or weight <= 0:
        return JSONResponse({"status": "error", "message": "Input tidak valid"}, status_code=400)

    # Simulasi perhitungan
    base_rate = 2.5
    distance_factor = len(origin) + len(destination)
    cost = round(weight * base_rate * distance_factor, 2)

    return {"freight_cost": cost}
