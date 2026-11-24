"""Community Renewable Energy Awareness and Management Portal (MESCOM region)."""
import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g
import calc

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-change-me")
DB = os.path.join(os.path.dirname(__file__), "community.db")

# MESCOM operating area (Karnataka coast + Malnad)
DISTRICTS = ["Dakshina Kannada", "Udupi", "Shivamogga", "Chikkamagaluru"]


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""CREATE TABLE IF NOT EXISTS households(
            id INTEGER PRIMARY KEY, name TEXT, locality TEXT, district TEXT,
            monthly_units REAL, solar_kw REAL, created TEXT DEFAULT CURRENT_TIMESTAMP)""")
    return g.db


@app.teardown_appcontext
def close(_):
    d = g.pop("db", None)
    if d:
        d.close()


def num(name, default=0.0, lo=0.0, hi=1e6):
    try:
        return min(max(float(request.values.get(name, default)), lo), hi)
    except (TypeError, ValueError):
        return default


@app.route("/")
def home():
    s = calc.solar(2, 87, 2.0, 58)
    return render_template("index.html", s=s, t=calc.TARIFF)


@app.route("/resources")
def resources():
    return render_template("resources.html")


@app.route("/bill", methods=["GET", "POST"])
def bill():
    units, kw, gj = num("units", 87, 0, 5000), num("kw", 2, 0.5, 50), num("gj", 58, 0, 200)
    arrears = num("arrears", 0, 0, 1e6)
    return render_template("bill.html", b=calc.bill(units, kw, gj, arrears),
                           f=dict(units=units, kw=kw, gj=gj, arrears=arrears), t=calc.TARIFF)


@app.route("/solar", methods=["GET", "POST"])
def solar():
    units, load, gj = num("units", 87, 0, 5000), num("load", 2, 0.5, 50), num("gj", 58, 0, 200)
    kw = num("kw", 2, 0.5, 20)
    s = calc.solar(kw, units, load, gj)
    return render_template("solar.html", s=s, f=dict(units=units, load=load, gj=gj, kw=kw),
                           assume=calc.SOLAR)


@app.route("/appliances")
def appliances():
    rows = []
    for name, old, new, hrs in calc.APPLIANCES:
        h = num("h_" + str(old), hrs, 0, 24)
        q = num("q_" + str(old), 1, 0, 100)
        rows.append(dict(name=name, key=old, hours=h, qty=q,
                         **calc.appliance_savings(old, new, h, q)))
    total = sum(r["rs"] for r in rows)
    return render_template("appliances.html", rows=rows, total=total)


@app.route("/community", methods=["GET", "POST"])
def community():
    d = db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:60]
        loc = request.form.get("locality", "").strip()[:60]
        dist = request.form.get("district")
        if not name or dist not in DISTRICTS:
            flash("Please enter a name and select a district.", "err")
        else:
            d.execute("INSERT INTO households(name,locality,district,monthly_units,solar_kw)"
                      " VALUES(?,?,?,?,?)",
                      (name, loc, dist, num("units", 0, 0, 5000), num("kw", 0, 0, 50)))
            d.commit()
            flash("Household added to the community tracker. Thank you!", "ok")
        return redirect(url_for("community"))
    rows = d.execute("SELECT * FROM households ORDER BY id DESC").fetchall()
    kw = sum(r["solar_kw"] or 0 for r in rows)
    gen = kw * calc.SOLAR["kwh_per_kwp_day"] * 365
    stats = dict(n=len(rows), kw=kw, gen=round(gen),
                 co2=round(gen * calc.SOLAR["co2_kg_per_kwh"] / 1000, 1),
                 save=round(gen * 7.5), units=round(sum(r["monthly_units"] or 0 for r in rows)))
    by_d = {x: sum(r["solar_kw"] or 0 for r in rows if r["district"] == x) for x in DISTRICTS}
    return render_template("community.html", rows=rows[:30], stats=stats,
                           by_d=by_d, districts=DISTRICTS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("DEBUG") == "1")
