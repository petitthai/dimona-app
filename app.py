import csv
import requests
from flask import Flask, render_template

app = Flask(__name__)

EMPLOYEE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"

def load_employees():
    response = requests.get(EMPLOYEE_CSV_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)

@app.route("/")
def index():
    employees = load_employees()
    return render_template("index.html", employees=employees)
