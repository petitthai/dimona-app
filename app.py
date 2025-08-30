from flask import Flask, render_template, request, send_file
from dimona_client import submit_dimona_form, build_dimona_payload
from utils import get_yesterday_formatted
import requests
import csv
from io import StringIO
import os
from generate_pdf import generate_pdf_for_worker  # externe functie voor PDF-generatie

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
            "id": row["Rijksregisternummer"],
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
    work_date = get_yesterday_formatted()
    shift_type = request.form.get('shift_type')
    
    if shift_type == "lunch":
        start_time = "12:00"
        end_time = "14:00"
    else:
        start_time = "17:30"
        end_time = "21:30"

    payload = build_dimona_payload(selected_worker_id, work_date, start_time, end_time)
    result_text = submit_dimona_form(payload)

    # Haal naam van werknemer voor weergave
    workers = fetch_workers()
    worker_name = next((f"{w['voornaam']} {w['achternaam']}" for w in workers if w["id"] == selected_worker_id), "Onbekend")

    return render_template(
        'result.html',
        result_text=result_text,
        worker_name=worker_name,
        worker_id=selected_worker_id
    )

@app.route('/download_pdf/<worker_id>')
def download_pdf(worker_id):
    pdf_path = f"dimona_result_{worker_id}.pdf"

    # Haal result_text op uit een tijdelijke opslag, of genereer opnieuw
    workers = fetch_workers()
    result_text = f"DIMONA resultaat voor {worker_id}"  # voorbeeld, kan dynamisch

    generate_pdf_for_worker(worker_id, pdf_path, result_text=result_text)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
