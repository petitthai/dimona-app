from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import datetime
import csv
import requests
from io import StringIO
import traceback

app = Flask(__name__)

# --- Configuration ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"
ENTERPRISE_NUMBER = "0766985433"


def load_workers():
    """Fetches and parses worker data from the Google Sheet CSV."""
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        csv_file = StringIO(response.text)
        reader = csv.DictReader(csv_file)
        workers = [
            {
                "id": row["Rijksregisternummer"].strip(),
                "name": f"{row['Voornaam'].strip()} {row['Achternaam'].strip()}",
                "inss": row["Rijksregisternummer"].strip(),
            }
            for row in reader
        ]
        return workers
    except Exception as e:
        print(f"Error loading workers CSV: {e}")
        return []


def send_dimona(enterprise_number, inss, date_str, shift):
    """
    Automates the Dimona submission process using Selenium.
    Returns a dictionary with the result.
    """
    if shift == "lunch":
        start_time, end_time = "12:00", "14:00"
    else:
        start_time, end_time = "17:30", "21:30"

    # More robust options for running headless Chrome in a container
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        print("Starting Selenium driver...")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)  # Increased wait time
        print("Driver started. Navigating to Dimona website...")

        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/")

        # Step 1: Enterprise Number
        print("Step 1: Filling enterprise number...")
        wait.until(EC.presence_of_element_located((By.ID, "idemployerNumber"))).send_keys(enterprise_number)
        driver.find_element(By.ID, "next").click()

        # Step 2: Next
        print("Step 2: Clicking next...")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='next']"))).click()

        # Step 3: INSS
        print("Step 3: Filling INSS...")
        wait.until(EC.presence_of_element_located((By.ID, "idinss"))).send_keys(inss)
        driver.find_element(By.ID, "next").click()

        # Step 4: Relation (Corrected to use Select class)
        print("Step 4: Selecting relation type...")
        select_com = Select(wait.until(EC.presence_of_element_located((By.ID, "comSelect"))))
        select_com.select_by_value("XXX")  # Selects "Andere"

        select_type = Select(wait.until(EC.presence_of_element_located((By.ID, "typeSelect"))))
        select_type.select_by_value("FLX")  # Selects "Flexi-Job"
        
        driver.find_element(By.ID, "next").click()

        # Step 5: Period
        print("Step 5: Filling period details...")
        wait.until(EC.element_to_be_clickable((By.ID, "idflexiRadioButtonsOnStep3_D"))).click()
        driver.find_element(By.ID, "iddateFlexi").send_keys(date_str)
        driver.find_element(By.NAME, "startTime0").send_keys(start_time)
        driver.find_element(By.NAME, "endTime0").send_keys(end_time)
        driver.find_element(By.ID, "next").click()

        # Step 6: Confirmation
        print("Step 6: Confirming submission...")
        wait.until(EC.url_contains("Step4SummaryFormAction.do"))
        wait.until(EC.presence_of_element_located((By.ID, "confirm"))).click()

        # Final Result
        print("Waiting for final confirmation page...")
        wait.until(EC.url_contains("DimonaResultPage"))
        
        print("Scraping result details...")
        confirmation_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".row-result")))
        confirmation_text = confirmation_element.text if confirmation_element else "Confirmation details not found."
        
        print("Submission successful.")
        return {"status": "success", "details": confirmation_text}

    except Exception as e:
        print("--- AN ERROR OCCURRED ---")
        print(str(e))
        traceback.print_exc()
        # Try to get a screenshot for debugging
        if driver:
            try:
                driver.save_screenshot('error_screenshot.png')
                print("Screenshot saved as error_screenshot.png")
            except:
                print("Could not save screenshot.")
        
        return {"status": "error", "details": "An internal error occurred during the automation. Check the server logs for more details."}

    finally:
        if driver:
            print("Closing Selenium driver.")
            driver.quit()

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

    workers = load_workers()
    worker = next((w for w in workers if w["id"] == worker_id), None)

    if not worker:
        return "Worker not found", 400

    result = send_dimona(ENTERPRISE_NUMBER, worker["inss"], date_str, shift)
    # The variable passed to the template is now named `result_data` to match the template's expectation.
    return render_template("result.html", worker=worker, result_data=result, shift=shift)

if __name__ == "__main__":
    app.run(debug=True)

