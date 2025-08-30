from flask import Flask, render_template, request, redirect, url_for
import csv
import requests
from io import StringIO
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

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
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    return render_template("index.html", workers=workers, yesterday=yesterday)

@app.route("/submit", methods=["POST"])
def submit():
    worker_id = request.form.get("worker_id")
    shift = request.form.get("shift")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    employer_number = request.form.get("employer_number")
    date_flexi = request.form.get("date_flexi")

    if not worker_id or not shift:
        return "Selecteer een werknemer en een shift.", 400

    # Selenium browser automation
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/")

        time.sleep(2)
        # Stap 1: Ondernemingsnummer
        driver.find_element(By.ID, "idemployerNumber").send_keys(employer_number)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 2: Volgende
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 3: Rijksregisternummer
        driver.find_element(By.ID, "idinss").send_keys(worker_id)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 4: Selecteer Andere en Flexi-Job
        Select(driver.find_element(By.ID, "comSelect")).select_by_value("XXX")
        Select(driver.find_element(By.ID, "typeSelect")).select_by_value("FLX")
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 5: Flexi dag en tijden
        driver.find_element(By.ID, "idflexiRadioButtonsOnStep3_D").click()
        driver.find_element(By.ID, "iddateFlexi").send_keys(date_flexi)
        driver.find_element(By.ID, "startTime0").send_keys(start_time)
        driver.find_element(By.ID, "endTime0").send_keys(end_time)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # Stap 6: Bevestigen
        driver.find_element(By.ID, "confirm").click()
        time.sleep(2)

        result_html = driver.page_source

    finally:
        driver.quit()

    return result_html

if __name__ == "__main__":
    app.run(debug=True)
