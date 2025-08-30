from flask import Flask, render_template, request
from dimona_client import submit_dimona_form, build_dimona_payload
from utils import get_yesterday_formatted
import requests
import csv
from io import StringIO

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"

def fetch_workers():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    csv_file = StringIO(response.text)
    reader = csv.DictReader(csv_file)
    workers = []
    for row in reader:
        workers.append({
            "id": row["INSZ"],  # Rijksregisternummer
            "voornaam": row["Voornaam"],
            "achternaam": row["Achternaam"]
        })
    return workers

@app.route('/')
def index():
    workers = fetch_workers()
    return render_template('index.html', workers=workers)

@app.route('/submit', methods=['POST'])
def submit():
    selected_worker_id = request.form.get('selected_worker')
    work_date = get_yesterday_formatted()  # altijd gisteren voor test
    shift_type = request.form.get('shift_type')
    
    if shift_type == "lunch":
        start_time = "12:00"
        end_time = "14:00"
    else:  # dinner
        start_time = "17:30"
        end_time = "21:30"

    payload = build_dimona_payload(selected_worker_id, work_date, start_time, end_time)
    result = submit_dimona_form(payload)
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
