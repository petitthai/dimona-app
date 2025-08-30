from flask import Flask, render_template, request, redirect, url_for
from dimona_client import submit_dimona_form
from utils import get_yesterday_formatted, build_dimona_payload
import csv
import requests

app = Flask(__name__)

EMPLOYEE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"

def load_employees():
    response = requests.get(EMPLOYEE_CSV_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)

@app.route("/", methods=["GET", "POST"])
def index():
    employees = load_employees()

    if request.method == "POST":
        selected_worker = request.form.get("selected_worker")
        if not selected_worker:
            return render_template("index.html", employees=employees, error="Selecteer eerst een werknemer!")

        # Build payload using yesterday
        date = get_yesterday_formatted()  # format: dd/mm/yyyy
        payload = build_dimona_payload(worker_id=selected_worker, date=date)

        # Submit form (for test, we can print result)
        result_html = submit_dimona_form(payload)
        return render_template("result.html", result=result_html)

    return render_template("index.html", employees=employees)
