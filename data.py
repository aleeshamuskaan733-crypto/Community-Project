"""Static content: renewable resources of the MESCOM service area."""

RESOURCES = [
    {"id": "solar", "name": "Solar (rooftop & community)", "icon": "☀️",
     "level": "High potential",
     "summary": "The most practical option for households, schools, farms and "
                "small businesses. Rooftop PV with net metering lets MESCOM "
                "consumers offset their own units and export the surplus.",
     "facts": ["Typical yield ≈ 3.8 kWh per kW per day (annual average), "
               "dropping sharply in the Jun-Sep monsoon.",
               "1 kW needs ~10 m² of shadow-free roof.",
               "Central PM Surya Ghar subsidy: ₹30,000/kW up to 2 kW + "
               "₹18,000 for the 3rd kW (max ₹78,000).",
               "Solar water heaters and solar pumps (PM-KUSUM) are also relevant."],
     "areas": "All five districts; Hassan and the Malnad interior get slightly "
              "more sunshine than the monsoon-heavy coast."},
    {"id": "hydro", "name": "Small & mini hydro", "icon": "💧",
     "level": "High potential (Western Ghats)",
     "summary": "Rivers and streams from the Western Ghats feed the largest "
                "renewable share of the region. Mini and micro hydro suit "
                "remote hamlets and community-managed schemes.",
     "facts": ["Large hydro in the area includes the Sharavathi and Linganamakki "
               "projects (Shivamogga district).",
               "Run-of-river micro hydro (5-100 kW) can power a village "
               "cluster, but output is seasonal.",
               "Needs a minimum head/flow survey and water-use clearance."],
     "areas": "Shivamogga, Chikkamagaluru, Dakshina Kannada hills, Hassan (Sakleshpur belt)."},
    {"id": "biomass", "name": "Biomass & biogas", "icon": "🌾",
     "level": "Medium potential",
     "summary": "Arecanut husk, coconut waste, rice husk, coffee-pulp and "
                "cattle dung are plentiful. Household biogas replaces LPG; "
                "larger plants can generate power.",
     "facts": ["A family biogas plant (2 m³) can supply most cooking needs from "
               "3-4 cattle's dung.",
               "Slurry is an excellent organic fertiliser.",
               "Community plants work well for dairy cooperatives and "
               "plantations."],
     "areas": "Arecanut/coconut belts of Dakshina Kannada, Udupi, Shivamogga; coffee estates of Chikkamagaluru and Hassan."},
    {"id": "wind", "name": "Wind", "icon": "🌬️",
     "level": "Low to moderate",
     "summary": "Large wind farms are concentrated elsewhere in Karnataka; the "
                "MESCOM area has limited sites, mostly ridge-tops and coastal "
                "strips. Small wind is rarely cost-effective for homes.",
     "facts": ["Needs a measured wind speed of ~5 m/s or more.",
               "Hybrid solar-wind streetlights are a good community pilot."],
     "areas": "Selected Western Ghats ridges and coastal pockets."},
]

TIPS = [
    ("Right-size before you buy", "Aim solar capacity at your average monthly "
     "units. The calculator shows the kW needed to offset ~100 % of use."),
    ("Check Gruha Jyothi first", "If you are on Gruha Jyothi, your payable bill "
     "may already be small; solar savings are then mainly the chargeable "
     "units above your entitlement."),
    ("Net metering", "Apply through MESCOM for a net-metering connection; "
     "surplus units are credited against future consumption."),
    ("Cut the base load", "5-star fans/BLDC fans, LED lighting and 5-star "
     "refrigerators reduce units without any generation investment."),
    ("Heat water with the sun", "A 100 L solar water heater can displace a "
     "geyser's 2-3 kWh per day."),
    ("Run heavy loads at midday", "Pumps, washing machines and irons match "
     "solar generation hours."),
    ("Keep panels clean and shade-free", "Dust and shade can cut output "
     "10-25 %. Rinse panels in the morning."),
    ("Watch power factor and load", "Power factor penalties and exceeding "
     "sanctioned load add charges to your bill."),
]

BILL_FIELDS = [
    ("Tariff / Sanctioned Load", "Your consumer category (domestic LT) and "
     "the kW contracted. Fixed charge = kW × ₹ per kW."),
    ("Prev / Pres Rdg", "Meter readings at the start and end of the billing "
     "cycle. The difference is your consumption in units (kWh)."),
    ("Gruha Jyothi entitlement / subsidy units", "Units covered free by the "
     "state scheme (up to 200, based on your 12-month average + 10 %)."),
    ("Fixed + Energy charges", "Fixed charge plus units × energy rate."),
    ("FPPCA", "Fuel & Power Purchase Cost Adjustment, per unit."),
    ("P & G surcharge", "Pension & gratuity surcharge, per unit."),
    ("Tax (9 %)", "Electricity tax levied on energy charges."),
    ("Sub Total 2", "The subsidy block deducted from Sub Total 1."),
    ("Net payable / Due date", "Amount to pay by the due date; interest or "
     "arrears may be added."),
]
