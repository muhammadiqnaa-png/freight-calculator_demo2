from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# ======== Simulasi user database sederhana ========
users = {"demo@gmail.com": "12345"}

# ======== Model request ========
class FreightRequest(BaseModel):
    origin: str
    destination: str
    weight: float

# ======== Routing dasar ========
@app.get("/")
def home():
    return {"status": "Backend aktif"}

@app.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")
    if email in users and users[email] == password:
        return {"status": "ok"}
    return {"error": "invalid credentials"}

@app.post("/register")
def register(data: dict):
    email = data.get("email")
    password = data.get("password")
    if email in users:
        return {"error": "already exists"}
    users[email] = password
    return {"status": "registered"}

@app.post("/calculate")
def calculate_freight(data: FreightRequest):
    # 🔹 RUMUS DEMO
    # misalnya ongkir = berat * 1.5 + panjang rute (dummy)
    base_rate = 1.5
    multiplier = len(data.origin) + len(data.destination)
    cost = data.weight * base_rate + multiplier
    return {"freight_cost": round(cost, 2)}
