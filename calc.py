"""Calculation engine for the MESCOM Community Renewable Energy Portal.

Tariff values are taken from the sample MESCOM LT bill (Gruha Jyothi consumer,
2 kW sanctioned load). They are plain constants so they can be updated when
KERC / MESCOM revise the tariff order.
"""

TARIFF = {
    "fixed_per_kw": 150.00,     # Rs / kW / month
    "energy_rate": 5.80,        # Rs / unit (kWh)
    "fppca": 0.26,              # Rs / unit  (fuel & power purchase cost adj.)
    "pg_surcharge": 0.35,       # Rs / unit  (P and G surcharge)
    "tax_pct": 9.0,             # % electricity tax
}
GRUHA_JYOTHI_CAP = 200          # free units / month ceiling under the scheme

# Solar assumptions for coastal Karnataka (Mangaluru / Udupi belt)
SOLAR = {
    "kwh_per_kwp_day": 4.2,     # net average yield after system losses
    "cost_per_kw": 55000,       # Rs / kW installed (residential, approx.)
    "co2_kg_per_kwh": 0.82,     # India grid emission factor (approx.)
    "export_rate": 3.50,        # Rs / unit paid for surplus (assumed net metering)
    "area_per_kw_sqft": 100,    # roof area needed per kWp
}
# Relative monthly generation (Jan..Dec); monsoon months are much lower.
MONTH_FACTOR = [1.12, 1.18, 1.18, 1.12, 1.00, 0.55, 0.45, 0.50, 0.80, 0.95, 1.05, 1.10]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _charges(units, kw, t=TARIFF):
    fixed = kw * t["fixed_per_kw"]
    energy = units * t["energy_rate"]
    fppca = units * t["fppca"]
    pg = units * t["pg_surcharge"]
    sub = fixed + energy + fppca + pg
    tax = sub * t["tax_pct"] / 100
    return {"fixed": fixed, "energy": energy, "fppca": fppca, "pg": pg,
            "tax": tax, "total": sub + tax}


def bill(units, kw, gj_units=0, arrears=0.0):
    """Estimate a monthly MESCOM bill, with Gruha Jyothi subsidy if eligible."""
    units, kw = max(0.0, units), max(0.0, kw)
    gj_units = min(max(0.0, gj_units), GRUHA_JYOTHI_CAP, units)
    gross = _charges(units, kw)
    if gj_units > 0:
        sub = _charges(gj_units, kw)          # subsidised share incl. fixed charge
        subsidy = min(sub["total"], gross["total"])
    else:
        subsidy = 0.0
    net = gross["total"] - subsidy + arrears
    return {"units": units, "kw": kw, "gj_units": gj_units,
            "chargeable": units - gj_units, "gross": gross,
            "subsidy": round(subsidy, 2), "arrears": arrears,
            "net": round(max(0.0, net), 2),
            "per_unit": round(gross["total"] / units, 2) if units else 0}


def solar(kw, monthly_units, kw_load=2.0, gj_units=0, budget_kw=None):
    """Estimate rooftop-solar generation, savings, subsidy, payback and CO2."""
    kw = max(0.0, kw)
    gen, rows, annual_new, annual_old = [], [], 0.0, 0.0
    for i, m in enumerate(MONTHS):
        g = kw * SOLAR["kwh_per_kwp_day"] * DAYS[i] * MONTH_FACTOR[i] / 1.0
        gen.append(g)
        old = bill(monthly_units, kw_load, gj_units)["net"]
        used = min(g, monthly_units)
        export = max(0.0, g - monthly_units)
        net_units = max(0.0, monthly_units - g)
        new_bill = bill(net_units, kw_load, min(gj_units, net_units))["net"]
        credit = export * SOLAR["export_rate"]
        saving = old - new_bill + credit
        annual_old += old
        annual_new += max(0.0, new_bill - credit)
        rows.append({"month": m, "gen": round(g), "old": round(old),
                     "new": round(max(0.0, new_bill - credit)),
                     "saving": round(saving), "export": round(export)})
    annual_gen = sum(gen)
    saving = annual_old - annual_new
    gross_cost = kw * SOLAR["cost_per_kw"]
    # PM Surya Ghar: Rs30,000/kW for first 2 kW, Rs18,000 for 3rd kW, cap Rs78,000
    subsidy = min(kw, 2) * 30000 + max(0.0, min(kw, 3) - 2) * 18000
    net_cost = max(0.0, gross_cost - subsidy)
    payback = net_cost / saving if saving > 0 else None
    return {"kw": kw, "rows": rows, "annual_gen": round(annual_gen),
            "annual_old": round(annual_old), "annual_new": round(annual_new),
            "saving": round(saving), "gross_cost": round(gross_cost),
            "subsidy": round(subsidy), "net_cost": round(net_cost),
            "payback": round(payback, 1) if payback else None,
            "co2_kg": round(annual_gen * SOLAR["co2_kg_per_kwh"]),
            "trees": round(annual_gen * SOLAR["co2_kg_per_kwh"] / 21),
            "area": round(kw * SOLAR["area_per_kw_sqft"]),
            "life_saving": round(saving * 25 - net_cost),
            "max_gen": max(gen) if gen else 0}


# Appliance upgrade savings: (name, old W, new W, default hours/day, tip)
APPLIANCES = [
    ("LED bulb instead of 60 W incandescent/CFL-equivalent", 60, 9, 5),
    ("BLDC ceiling fan instead of regular fan", 75, 28, 10),
    ("5-star inverter AC instead of old 3-star", 1500, 900, 6),
    ("Solar water heater instead of electric geyser", 2000, 0, 1),
    ("5-star refrigerator instead of 10-year-old model", 150, 70, 24),
]


def appliance_savings(old_w, new_w, hours, qty=1):
    kwh_month = (old_w - new_w) * hours * 30 * qty / 1000
    return {"kwh": round(kwh_month, 1),
            "rs": round(kwh_month * (TARIFF["energy_rate"] + TARIFF["fppca"]
                                      + TARIFF["pg_surcharge"]) * 1.09)}
