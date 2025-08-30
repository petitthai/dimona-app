import time
import csv
from io import StringIO
import requests
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
            "id": row["Rijksregisternummer"],  # Rijksregisternummer
            "voornaam": row["Voornaam"],
            "achternaam": row["Achternaam"]
        })
    return workers

@app.route("/", methods=["GET"])
def index():
    workers = fetch_workers()
    return render_template("index.html", workers=workers)

@app.route("/submit", methods=["POST"])
def submit():
    selected_worker_id = request.form.get("worker_id")
    if not selected_worker_id:
        return "Geen werknemer geselecteerd!", 400

    employer_number = request.form.get("employer_number")
    date_flexi = request.form.get("date_flexi")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # kan weggelaten worden om browser te zien
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Stap 1: Ondernemingsnummer invullen en volgende klikken
        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/")  # vervang door juiste startpagina
        time.sleep(2)
        driver.find_element(By.ID, "idemployerNumber").send_keys(employer_number)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 2: Volgende klikken
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 3: Rijksregisternummer invullen
        driver.find_element(By.ID, "idinss").send_keys(selected_worker_id)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 4: Selecteer "Andere" en "FLX"
        driver.find_element(By.ID, "comSelect").send_keys("XXX")  # Andere
        driver.find_element(By.ID, "typeSelect").send_keys("FLX")
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 5: Dag selecteren en tijden invullen
        driver.find_element(By.ID, "idflexiRadioButtonsOnStep3_D").click()
        time.sleep(1)
        driver.find_element(By.ID, "iddateFlexi").send_keys(date_flexi)
        driver.find_element(By.NAME, "startTime0").send_keys(start_time)
        driver.find_element(By.NAME, "endTime0").send_keys(end_time)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 6: Bevestigen
        driver.find_element(By.ID, "confirm").click()
        time.sleep(2)

        # Resultaatpagina ophalen
        result_html = driver.page_source
        return result_html

    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(debug=True)
