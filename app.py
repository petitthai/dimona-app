from flask import Flask, render_template, request, send_file
from dimona_client import submit_dimona_form, build_dimona_payload
from utils import get_yesterday_formatted
from generate_pdf import generate_pdf_for_worker
import requests
import csv
from io import StringIO
import os

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
    else:  # dinner
        start_time = "17:30"
        end_time = "21:30"

    payload = build_dimona_payload(selected_worker_id, work_date, start_time, end_time)
    result_html = submit_dimona_form(payload)

    # PDF genereren
    pdf_filename = f"dimona_{selected_worker_id}_{work_date}.pdf"
    generate_pdf_for_worker(result_html, pdf_filename)

    return render_template('result.html', result_html=result_html, pdf_file=pdf_filename)

@app.route('/download/<pdf_file>')
def download_pdf(pdf_file):
    # Veilig pad construeren
    safe_path = os.path.abspath(pdf_file)
    return send_file(safe_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
