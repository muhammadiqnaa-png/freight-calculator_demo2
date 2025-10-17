def calculate_freight(params, mode="Owner"):
    # Hitung Sailing Time
    sailing_time = (params['distance_pol_pod']/params['speed_laden']) + (params['distance_pod_pol']/params['speed_ballast'])
    
    total_voyage_days = (sailing_time / 24) + (params['port_stay_pol'] + params['port_stay_pod'])
    total_consumption = sailing_time * params['consumption_fuel'] + (params['port_stay_pol'] + params['port_stay_pod']) * 120
    
    charter_cost = (params['charter_hire']/30) * total_voyage_days
    bunker_cost = total_consumption * params['price_bunker']
    port_cost = params['port_cost_pol'] + params['port_cost_pod']
    premi_cost = params['distance_pol_pod'] * params['premi']
    crew_cost = (params['crew_cost']/30) * total_voyage_days
    insurance_cost = (params['insurance']/30) * total_voyage_days
    docking_cost = (params['docking']/30) * total_voyage_days
    maintenance_cost = (params['maintenance']/30) * total_voyage_days
    asist_tug = params['asist_tug']

    if mode=="Charter":
        total_cost = charter_cost + bunker_cost + port_cost + premi_cost + asist_tug
    else:
        total_cost = charter_cost + bunker_cost + crew_cost + port_cost + premi_cost + asist_tug + insurance_cost + docking_cost + maintenance_cost

    freight_per_unit = total_cost / params['qty_cargo'] if params['qty_cargo']>0 else 0

    # Profit table 0-50%
    profit_table = []
    for p in range(0,51):
        revenue = freight_per_unit * params['qty_cargo'] * (1 + p/100)
        pph = revenue * 0.012
        profit = revenue - total_cost - pph
        profit_table.append({"Percent":p,"Revenue":revenue,"PPH":pph,"Profit":profit})

    return {
        "sailing_time": sailing_time,
        "total_voyage_days": total_voyage_days,
        "total_consumption": total_consumption,
        "total_cost": total_cost,
        "freight_per_unit": freight_per_unit,
        "profit_table": profit_table
    }
