from flask import Flask, render_template, request
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import datetime

app = Flask(__name__)

# CSV Google Sheets link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"

# Ondernemingsnummer vast
ENTERPRISE_NUMBER = "0766985433"


def load_workers():
    df = pd.read_csv(CSV_URL)
    workers = df.to_dict(orient="records")
    return workers


def send_dimona(enterprise_number, inss, date_str, shift):
    """
    enterprise_number: ondernemingsnummer (string)
    inss: rijksregisternummer werknemer (string)
    date_str: datum in formaat dd/mm/jjjj (string)
    shift: 'lunch' of 'dinner'
    """

    # Shift tijden
    if shift == "lunch":
        start_time, end_time = "12:00", "14:00"
    else:
        start_time, end_time = "17:30", "21:30"

    # Selenium driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # headless run
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/")
        time.sleep(2)

        # STAP 1: ondernemingsnummer
        driver.find_element(By.ID, "idemployerNumber").send_keys(enterprise_number)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # STAP 2: volgende
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # STAP 3: INSS
        driver.find_element(By.ID, "idinss").send_keys(inss)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # STAP 4: selecteer "Andere - XXX" en "Flexi"
        Select(driver.find_element(By.ID, "comSelect")).select_by_value("XXX")
        time.sleep(1)
        Select(driver.find_element(By.ID, "typeSelect")).select_by_value("FLX")
        time.sleep(1)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # STAP 5: dag, datum & uren
        driver.find_element(By.ID, "idflexiRadioButtonsOnStep3_D").click()
        time.sleep(1)
        driver.find_element(By.ID, "iddateFlexi").send_keys(date_str)
        driver.find_element(By.NAME, "startTime0").send_keys(start_time)
        driver.find_element(By.NAME, "endTime0").send_keys(end_time)
        driver.find_element(By.ID, "next").click()
        time.sleep(2)

        # STAP 6: bevestigen
        driver.find_element(By.ID, "confirm").click()
        time.sleep(2)

        # Resultaat HTML
        result_html = driver.page_source

    finally:
        driver.quit()

    return result_html


@app.route("/")
def index():
    workers = load_workers()
    today = datetime.date.today().strftime("%d/%m/%Y")
    return render_template("form.html", workers=workers, today=today)


@app.route("/submit", methods=["POST"])
def submit():
    worker_id = request.form.get("worker_id")
    shift = request.form.get("shift")
    date_str = request.form.get("date")

    # Worker ophalen uit CSV
    workers = load_workers()
    worker = next((w for w in workers if str(w["id"]) == str(worker_id)), None)

    if not worker:
        return "Werknemer niet gevonden", 400

    inss = worker["inss"]  # Rijksregisternummer
    result_html = send_dimona(ENTERPRISE_NUMBER, inss, date_str, shift)

    return render_template("result.html", worker=worker, result_html=result_html)


if __name__ == "__main__":
    app.run(debug=True)
