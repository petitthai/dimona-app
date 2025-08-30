import time
import csv
from io import StringIO
import requests
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"  # vervang door je echte CSV URL

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

@app.route("/")
def index():
    workers = fetch_workers()
    return render_template("index.html", workers=workers)

@app.route("/submit", methods=["POST"])
def submit():
    selected_worker_id = request.form["worker_id"]
    employer_number = request.form["employer_number"]
    date_flexi = request.form["date_flexi"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    # Selenium setup
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://dimona.socialsecurity.be/dimona/unsecured/Step0EmployerFormAction.do")

    # Stap 1: Ondernemingsnummer invullen en volgende
    driver.find_element(By.ID, "idemployerNumber").send_keys(employer_number)
    driver.find_element(By.ID, "next").click()
    time.sleep(2)

    # Stap 2: Klik volgende
    driver.find_element(By.ID, "next").click()
    time.sleep(2)

    # Stap 3: Rijksregisternummer invullen
    driver.find_element(By.ID, "idinss").send_keys(selected_worker_id)
    driver.find_element(By.ID, "next").click()
    time.sleep(2)

    # Stap 4: Selecteer "Andere" en "FLX"
    Select(driver.find_element(By.ID, "comSelect")).select_by_value("XXX")
    Select(driver.find_element(By.ID, "typeSelect")).select_by_value("FLX")
    driver.find_element(By.ID, "next").click()
    time.sleep(2)

    # Stap 5: Flexi-job datum en uren invullen
    driver.find_element(By.ID, "idflexiRadioButtonsOnStep3_D").click()
    driver.find_element(By.ID, "iddateFlexi").send_keys(date_flexi)
    driver.find_element(By.NAME, "startTime0").send_keys(start_time)
    driver.find_element(By.NAME, "endTime0").send_keys(end_time)
    driver.find_element(By.ID, "next").click()
    time.sleep(2)

    # Stap 6: Bevestigen
    driver.find_element(By.ID, "confirm").click()
    time.sleep(2)

    # Laat resultaatpagina zien in browser
    return "Dimona formulier verzonden! Controleer de browser voor resultaat."

if __name__ == "__main__":
    app.run(debug=True)
