from flask import Flask, render_template, request, redirect, url_for
import requests
import csv
from io import StringIO
from datetime import datetime, timedelta
from dimona_client import submit_dimona_form
from utils import get_yesterday_formatted, parse_time_to_hhmm, build_dimona_payload

app = Flask(__name__)

# CSV URL van de Google Sheet
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"

def fetch_employees():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    csv_text = response.text
    f = StringIO(csv_text)
    reader = csv.DictReader(f)
    employees = []
    for row in reader:
        employees.append({
            "worker_id": row.get("Rijksregisternummer"),
            "name": f"{row.get('Voornaam')} {row.get('Naam')}"
        })
    return employees

@app.route("/", methods=["GET"])
def index():
    employees = fetch_employees()
    return render_template("index.html", employees=employees)

@app.route("/submit", methods=["POST"])
def submit():
    worker_id = request.form.get("worker_id")
    shift_type = request.form.get("shift_type")  # lunch/dinner
    # gebruik gisteren voor test
    work_date = get_yesterday_formatted()

    start_time, end_time = ("12:00", "14:00") if shift_type == "lunch" else ("17:30", "21:30")
    payload = build_dimona_payload(worker_id, work_date, start_time, end_time)
    
    result = submit_dimona_form(payload)
    return render_template("result.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)

