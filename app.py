from flask import Flask, render_template, request
import csv
import requests
from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

app = Flask(__name__, template_folder='templates')

# --- Configuration ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"
ENTERPRISE_NUMBER = "0766985433"


def load_workers():
    """Loads worker data from the Google Sheet."""
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        csv_file = StringIO(response.text)
        reader = csv.DictReader(csv_file)
        workers = []
        for row in reader:
            full_name = f"{row['Voornaam'].strip()} {row['Achternaam'].strip()}"
            inss_number = row['Rijksregisternummer'].strip()
            workers.append({'id': inss_number, 'name': full_name, 'inss': inss_number})
        return workers
    except Exception as e:
        print(f"Error loading workers: {e}")
        return []


def send_dimona(enterprise_number, inss, date_str, shift):
    """Automates the Dimona declaration process using Selenium."""
    shift_times = {"lunch": ("12:00", "14:00"), "dinner": ("17:30", "21:30")}
    start_time, end_time = shift_times.get(shift, (None, None))
    if not start_time: raise ValueError("Invalid shift.")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/")

        # Step 1: Enterprise number
        wait.until(EC.presence_of_element_located((By.ID, "idemployerNumber"))).send_keys(enterprise_number)
        driver.find_element(By.ID, "next").click()

        # Step 2: Next
        wait.until(EC.element_to_be_clickable((By.ID, "next"))).click()

        # Step 3: INSS
        wait.until(EC.presence_of_element_located((By.ID, "idinss"))).send_keys(inss)
        driver.find_element(By.ID, "next").click()

        # Step 4: Commission and Type
        wait.until(EC.presence_of_element_located((By.ID, "comSelect")))
        Select(driver.find_element(By.ID, "comSelect")).select_by_value("XXX")
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "typeSelect")).select_by_value("FLX")
        driver.find_element(By.ID, "next").click()

        # Step 5: Date and hours
        wait.until(EC.presence_of_element_located((By.ID, "idflexiRadioButtonsOnStep3_D"))).click()
        time.sleep(0.5)
        driver.find_element(By.ID, "iddateFlexi").send_keys(date_str)
        driver.find_element(By.NAME, "startTime0").send_keys(start_time)
        driver.find_element(By.NAME, "endTime0").send_keys(end_time)
        driver.find_element(By.ID, "next").click()

        # Step 6: Confirm
        wait.until(EC.element_to_be_clickable((By.ID, "confirm"))).click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver.page_source
    finally:
        driver.quit()


@app.route("/")
def index():
    """Renders the main form with date options."""
    workers = load_workers()
    today = datetime.date.today()
    date_options = {
        "today": today.strftime("%d/%m/%Y"),
        "tomorrow": (today + datetime.timedelta(days=1)).strftime("%d/%m/%Y")
    }
    return render_template("form.html", workers=workers, date_options=date_options)


@app.route("/submit", methods=["POST"])
def submit():
    """Handles form submission and displays the result."""
    worker_id = request.form.get("worker_id")
    shift = request.form.get("shift")
    date_str = request.form.get("date")

    workers = load_workers()
    worker = next((w for w in workers if str(w["id"]) == str(worker_id)), None)

    if not worker:
        return "Error: Worker not found.", 400

    try:
        result_html = send_dimona(ENTERPRISE_NUMBER, worker["inss"], date_str, shift)
        return render_template("result.html", worker=worker, result_html=result_html, date=date_str, shift=shift)
    except Exception as e:
        print(f"An error occurred during Dimona submission: {e}")
        return f"An error occurred: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)

