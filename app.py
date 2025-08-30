from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import csv
from io import StringIO
from datetime import date, timedelta

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

def get_workers():
    return fetch_workers()

@app.route("/", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        worker_id = request.form["worker_id"]
        shift = request.form["shift"]  # lunch of dinner

        driver = webdriver.Chrome()
        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/")

        # Vul bedrijfsnummer
        driver.find_element(By.ID, "comSelect").send_keys("0766985433")

        # Vul datum (gisteren)
        yesterday = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
        driver.find_element(By.ID, "dateInput").send_keys(yesterday)

        # Vul tijd
        if shift == "lunch":
            driver.find_element(By.ID, "startTime").send_keys("12:00")
            driver.find_element(By.ID, "endTime").send_keys("14:00")
        else:
            driver.find_element(By.ID, "startTime").send_keys("17:30")
            driver.find_element(By.ID, "endTime").send_keys("21:30")

        # Vul werknemer
        driver.find_element(By.ID, "workerSelect").send_keys(worker_id)

        # Verzenden
        driver.find_element(By.ID, "submitBtn").click()

        # Wacht tot resultaatpagina geladen is
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        result_html = driver.page_source
        driver.quit()

        return render_template("result.html", result_html=result_html)

    return render_template("form.html", workers=get_workers())

@app.route("/new")
def new_submission():
    return redirect(url_for("submit"))

if __name__ == "__main__":
    app.run(debug=True)
