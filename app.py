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
# Link to your Google Sheet with worker data (must be public)
# The sheet should have columns: 'Rijksregisternummer', 'Voornaam', 'Achternaam'
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJbpHVppuTI8jaWb-kYI_THslQpw_j9LUlzAsXC7-rA6Cur8uV9M524hDVsMYr7T-zjVk0GcQVe8nP/pub?gid=0&single=true&output=csv"

# Your company's enterprise number
ENTERPRISE_NUMBER = "0766985433"


def load_workers():
    """Loads worker data from the Google Sheet using requests and csv."""
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()  # Raise an exception for bad status codes

        csv_file = StringIO(response.text)
        reader = csv.DictReader(csv_file)
        
        workers = []
        for row in reader:
            # Combine Voornaam and Achternaam for the display name.
            # Use Rijksregisternummer for both the unique ID and the INSS value.
            full_name = f"{row['Voornaam'].strip()} {row['Achternaam'].strip()}"
            inss_number = row['Rijksregisternummer'].strip()
            
            workers.append({
                'id': inss_number,
                'name': full_name,
                'inss': inss_number
            })
        return workers
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google Sheet: {e}")
        return []
    except KeyError as e:
        print(f"Error parsing CSV: Missing expected column - {e}. Check your CSV for 'Rijksregisternummer', 'Voornaam', and 'Achternaam'.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in load_workers: {e}")
        return []


def send_dimona(enterprise_number, inss, date_str, shift):
    """
    Automates the Dimona declaration process using Selenium.

    Args:
        enterprise_number (str): The company's enterprise number.
        inss (str): The worker's national register number.
        date_str (str): The declaration date in 'dd/mm/yyyy' format.
        shift (str): The shift, either 'lunch' or 'dinner'.

    Returns:
        str: The HTML source of the final result page.
    """

    # Define start and end times based on the selected shift
    shift_times = {
        "lunch": ("12:00", "14:00"),
        "dinner": ("17:30", "21:30")
    }
    start_time, end_time = shift_times.get(shift, (None, None))
    if not start_time:
        raise ValueError("Invalid shift provided.")

    # Configure Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Run in headless mode (no browser window)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # Use a wait object for more reliable automation
    wait = WebDriverWait(driver, 10)  # Wait for up to 10 seconds

    try:
        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/")

        # --- Stap 1: Fill in enterprise number ---
        wait.until(EC.presence_of_element_located((By.ID, "idemployerNumber"))).send_keys(enterprise_number)
        driver.find_element(By.ID, "next").click()

        # --- Stap 2: Click 'Next' on the employer details page ---
        wait.until(EC.element_to_be_clickable((By.ID, "next"))).click()

        # --- Stap 3: Fill in worker's INSS number ---
        wait.until(EC.presence_of_element_located((By.ID, "idinss"))).send_keys(inss)
        driver.find_element(By.ID, "next").click()

        # --- Stap 4: Select commission and contract type ---
        wait.until(EC.presence_of_element_located((By.ID, "comSelect")))
        Select(driver.find_element(By.ID, "comSelect")).select_by_value("XXX")
        # Short wait for any potential JS updates on the page
        time.sleep(0.5)
        Select(driver.find_element(By.ID, "typeSelect")).select_by_value("FLX")
        driver.find_element(By.ID, "next").click()

        # --- Stap 5: Fill in date and shift hours ---
        wait.until(EC.presence_of_element_located((By.ID, "idflexiRadioButtonsOnStep3_D"))).click()
        time.sleep(0.5) # Wait for date field to become active
        driver.find_element(By.ID, "iddateFlexi").send_keys(date_str)
        driver.find_element(By.NAME, "startTime0").send_keys(start_time)
        driver.find_element(By.NAME, "endTime0").send_keys(end_time)
        driver.find_element(By.ID, "next").click()

        # --- Stap 6: Confirm the declaration ---
        wait.until(EC.element_to_be_clickable((By.ID, "confirm"))).click()

        # Wait for the result page to load and get its source
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        result_html = driver.page_source

    finally:
        driver.quit()

    return result_html


@app.route("/")
def index():
    """Renders the main form page."""
    workers = load_workers()
    today = datetime.date.today().strftime("%d/%m/%Y")
    return render_template("form.html", workers=workers, today=today)


@app.route("/submit", methods=["POST"])
def submit():
    """Handles form submission and displays the result."""
    worker_id = request.form.get("worker_id") # This will be the INSS number from the form
    shift = request.form.get("shift")
    date_str = request.form.get("date")

    workers = load_workers()
    # Find the worker using the 'id' which is the INSS number
    worker = next((w for w in workers if str(w["id"]) == str(worker_id)), None)

    if not worker:
        return "Error: Worker not found.", 400

    try:
        # The 'inss' field already contains the correct number
        inss = worker["inss"]
        print(f"Submitting Dimona for {worker['name']} ({inss}) on {date_str} for {shift} shift.")
        result_html = send_dimona(ENTERPRISE_NUMBER, inss, date_str, shift)
        return render_template("result.html", worker=worker, result_html=result_html, date=date_str, shift=shift)
    except Exception as e:
        print(f"An error occurred during Dimona submission: {e}")
        return f"An error occurred: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)


