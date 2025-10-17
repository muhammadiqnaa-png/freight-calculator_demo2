import pandas as pd

def calculate_freight(speed_laden, speed_ballast, fuel, bunker_price,
                      charter, crew, insurance, docking, maintenance,
                      port_pol, port_pod, tug, premi, other, stay_pol, stay_pod,
                      cargo_type, qty, dist_pol_pod, dist_pod_pol):

    sailing_time = (dist_pol_pod / speed_laden) + (dist_pod_pol / speed_ballast)
    total_days = (sailing_time / 24) + (stay_pol + stay_pod)
    total_fuel = (sailing_time * fuel) + ((stay_pol + stay_pod) * 120)

    charter_cost = (charter / 30) * total_days
    bunker_cost = total_fuel * bunker_price
    port_cost = port_pol + port_pod
    premi_cost = dist_pol_pod * premi
    crew_cost = (crew / 30) * total_days
    insurance_cost = (insurance / 30) * total_days
    docking_cost = (docking / 30) * total_days
    maintenance_cost = (maintenance / 30) * total_days

    total_cost = (charter_cost + bunker_cost + crew_cost + port_cost + premi_cost +
                  tug + insurance_cost + docking_cost + maintenance_cost + other)

    freight_mt = total_cost / qty if qty else 0

    results = pd.DataFrame({
        "Keterangan": [
            "Sailing Time (Hours)", "Total Voyage Days", "Total Consumption (liter)",
            "Charter Cost", "Bunker Cost", "Crew Cost", "Port Cost",
            "Premi Cost", "Insurance Cost", "Docking Saving", "Maintenance Cost", "Total Cost", "Freight (per MT/M3)"
        ],
        "Hasil": [
            sailing_time, total_days, total_fuel, charter_cost, bunker_cost, crew_cost,
            port_cost, premi_cost, insurance_cost, docking_cost, maintenance_cost, total_cost, freight_mt
        ]
    })

    profit_rows = []
    for p in range(0, 55, 5):
        revenue = freight_mt * qty * (1 + p / 100)
        pph = revenue * 0.012
        profit = revenue - pph - total_cost
        profit_rows.append({"Profit %": p, "Revenue": revenue, "PPH 1.2%": pph, "Net Profit": profit})

    profit_table = pd.DataFrame(profit_rows)
    return results, profit_table
