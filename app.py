from flask import Flask, render_template, request, redirect, url_for
import requests
import csv
from io import StringIO

app = Flask(__name__)

# CSV URL van Google Sheets
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"

def get_workers():
    """Haal werknemers op uit de CSV."""
    response = requests.get(CSV_URL)
    response.raise_for_status()
    csv_file = StringIO(response.text)
    reader = csv.DictReader(csv_file)
    workers = []
    for row in reader:
        workers.append({
            "id": row["Rijksregisternummer"],
            "voornaam": row["Voornaam"],
            "achternaam": row["Achternaam"]
        })
    return workers

@app.route("/", methods=["GET", "POST"])
def form():
    workers = get_workers()
    if request.method == "POST":
        selected_worker_ids = request.form.getlist("worker_id")
        meal = request.form.get("meal")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        # Stuur gegevens door naar de resultaatpagina
        return render_template("result.html",
                               workers=[w for w in workers if w["id"] in selected_worker_ids],
                               meal=meal,
                               date=date,
                               start_time=start_time,
                               end_time=end_time)
    return render_template("form.html", workers=workers)

if __name__ == "__main__":
    app.run(debug=True)
