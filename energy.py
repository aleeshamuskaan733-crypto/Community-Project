"""Energy / bill calculation engine for the MESCOM community portal.

The bill model reproduces the structure of a MESCOM LT domestic bill with the
Gruha Jyothi scheme (fixed charge + energy charge + FPPCA + P&G surcharge,
9 % tax on energy charges, then a "subsidy" block that is deducted).
All rates are defaults taken from a sample bill and are editable in the UI.
"""

DEFAULT_TARIFF = {
    "fixed_per_kw": 150.0,   # Rs / kW / month
    "energy_rate": 5.80,     # Rs / unit
    "fppca": 0.26,           # Rs / unit  (fuel & power purchase cost adj.)
    "pg_surcharge": 0.35,    # Rs / unit  (pension & gratuity surcharge)
    "tax_pct": 9.0,          # % on energy charges
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Indicative rooftop-solar yield (kWh per kW per month), coastal/Malnad Karnataka.
# Monsoon months (Jun-Sep) are much lower.  Replace with PVWatts/MNRE data for design.
SOLAR_YIELD = [135, 140, 150, 145, 130, 85, 70, 75, 105, 115, 115, 125]

# District multipliers (indicative) for the MESCOM service area.
DISTRICTS = {
    "Dakshina Kannada": 1.00,
    "Udupi": 1.00,
    "Shivamogga": 1.03,
    "Chikkamagaluru": 1.03,
    "Hassan": 1.06,
}

GRID_CO2_KG_PER_KWH = 0.72   # approx. Indian grid emission factor
CO2_PER_TREE_KG_YEAR = 21.0  # approx. absorption of a mature tree


def _r(x):
    return round(x + 1e-9, 2)


def charges(units, load_kw, tariff, include_fixed=True):
    energy = units * tariff["energy_rate"]
    fixed = load_kw * tariff["fixed_per_kw"] if include_fixed else 0.0
    fppca = units * tariff["fppca"]
    pg = units * tariff["pg_surcharge"]
    tax = energy * tariff["tax_pct"] / 100.0
    return {"fixed": _r(fixed), "energy": _r(energy), "fppca": _r(fppca),
            "pg": _r(pg), "tax": _r(tax),
            "total": _r(fixed + energy + fppca + pg + tax)}


def bill(units, load_kw, tariff=None, gruha_jyothi=False, entitlement=0.0):
    """Monthly bill. With Gruha Jyothi, `entitlement` units (max 200) and the
    fixed charge are subsidised (this reproduces the sample MESCOM bill)."""
    t = {**DEFAULT_TARIFF, **(tariff or {})}
    gross = charges(units, load_kw, t)
    sub = {"total": 0.0, "units": 0.0}
    if gruha_jyothi and entitlement > 0:
        sub_units = min(units, min(entitlement, 200))
        sub = charges(sub_units, load_kw, t)
        sub["units"] = sub_units
    return {"gross": gross, "subsidy": sub,
            "payable": _r(max(0.0, gross["total"] - sub["total"]))}


def pm_surya_ghar_subsidy(kw):
    """Central subsidy for residential rooftop solar (PM Surya Ghar scheme)."""
    if kw <= 0:
        return 0.0
    return float(min(kw, 2) * 30000 + max(0, min(kw, 3) - 2) * 18000)


def solar_estimate(units, load_kw, solar_kw, district="Dakshina Kannada",
                   tariff=None, gruha_jyothi=False, entitlement=0.0,
                   cost_per_kw=55000.0, apply_subsidy=True,
                   annual_degradation=0.5, escalation=3.0):
    """12-month net-metering estimate + 25-year payback."""
    factor = DISTRICTS.get(district, 1.0)
    t = {**DEFAULT_TARIFF, **(tariff or {})}
    credit = 0.0
    rows = []
    base_total = new_total = gen_total = 0.0
    for i, m in enumerate(MONTHS):
        gen = solar_kw * SOLAR_YIELD[i] * factor
        net = units - gen - credit
        credit = max(0.0, -net)          # surplus carried forward (net metering)
        net = max(0.0, net)
        before = bill(units, load_kw, t, gruha_jyothi, entitlement)["payable"]
        after = bill(net, load_kw, t, gruha_jyothi, entitlement)["payable"]
        rows.append({"month": m, "generation": _r(gen), "net_units": _r(net),
                     "bill_before": before, "bill_after": after})
        base_total += before; new_total += after; gen_total += gen
    saving = base_total - new_total
    cost = solar_kw * cost_per_kw
    subsidy = pm_surya_ghar_subsidy(solar_kw) if apply_subsidy else 0.0
    net_cost = max(0.0, cost - subsidy)
    # 25-year cash flow
    cum, payback, s = -net_cost, None, saving
    for y in range(1, 26):
        cum += s
        if payback is None and cum >= 0 and s > 0:
            prev = cum - s
            payback = (y - 1) + (-prev / s)
        s = s * (1 - annual_degradation / 100) * (1 + escalation / 100)
    return {
        "rows": rows,
        "annual_generation": _r(gen_total),
        "annual_bill_before": _r(base_total),
        "annual_bill_after": _r(new_total),
        "annual_saving": _r(saving),
        "co2_kg": _r(gen_total * GRID_CO2_KG_PER_KWH),
        "trees": _r(gen_total * GRID_CO2_KG_PER_KWH / CO2_PER_TREE_KG_YEAR),
        "system_cost": _r(cost), "subsidy": _r(subsidy), "net_cost": _r(net_cost),
        "payback_years": None if payback is None else _r(payback),
        "gain_25y": _r(cum),
        "suggested_kw": suggest_kw(units, district),
    }


def suggest_kw(units, district="Dakshina Kannada"):
    """kW needed to offset ~100 % of annual consumption."""
    factor = DISTRICTS.get(district, 1.0)
    per_kw_year = sum(SOLAR_YIELD) * factor
    return round(units * 12 / per_kw_year, 1)


def community_estimate(households, avg_units, adoption_pct, kw_per_home,
                       district="Dakshina Kannada", community_kw=0.0,
                       biogas_homes=0, tariff=None, cost_per_kw=55000.0):
    t = {**DEFAULT_TARIFF, **(tariff or {})}
    factor = DISTRICTS.get(district, 1.0)
    annual_per_kw = sum(SOLAR_YIELD) * factor
    adopters = round(households * adoption_pct / 100.0)
    roof_kwh = adopters * kw_per_home * annual_per_kw
    comm_kwh = community_kw * annual_per_kw
    # Offsetting grid units saves about energy + FPPCA + P&G + tax per unit
    per_unit = (t["energy_rate"] * (1 + t["tax_pct"] / 100)
                + t["fppca"] + t["pg_surcharge"])
    biogas_kwh_eq = biogas_homes * 365 * 1.2  # ~ 1.2 kWh/day LPG-equivalent
    total = roof_kwh + comm_kwh
    demand = households * avg_units * 12
    return {
        "adopters": adopters,
        "rooftop_kwh": _r(roof_kwh), "community_kwh": _r(comm_kwh),
        "total_kwh": _r(total), "biogas_kwh_eq": _r(biogas_kwh_eq),
        "community_demand_kwh": _r(demand),
        "share_pct": _r(100 * total / demand) if demand else 0,
        "money_saved": _r(total * per_unit),
        "per_unit_value": _r(per_unit),
        "co2_tonnes": _r((total + biogas_kwh_eq) * GRID_CO2_KG_PER_KWH / 1000),
        "trees": round((total + biogas_kwh_eq) * GRID_CO2_KG_PER_KWH / CO2_PER_TREE_KG_YEAR),
        "investment": _r((adopters * kw_per_home + community_kw) * cost_per_kw),
        "installed_kw": _r(adopters * kw_per_home + community_kw),
    }
