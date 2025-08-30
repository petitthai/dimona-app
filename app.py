from flask import Flask, render_template, request
from utils import get_yesterday_formatted
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import requests
from io import StringIO

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

@app.route('/')
def index():
    workers = fetch_workers()
    return render_template('index.html', workers=workers)

@app.route('/submit', methods=['POST'])
def submit():
    selected_worker_id = request.form.get('selected_worker')
    work_date = get_yesterday_formatted()  # altijd gisteren voor test
    shift_type = request.form.get('shift_type')
    
    if shift_type == "lunch":
        start_time = "12:00"
        end_time = "14:00"
    else:  # dinner
        start_time = "17:30"
        end_time = "21:30"

    # --- Start Selenium browser automation ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # run in background
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open DIMONA summary page (direct unsecured submission URL)
        driver.get("https://dimona.socialsecurity.be/dimona/unsecured/Step4SummaryFormAction.do")

        # Wait until page loads (adjust selectors if needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        # Fill the form fields (example — adjust field names)
        driver.execute_script(f"document.querySelector('[name=\"employeeId\"]').value = '{selected_worker_id}'")
        driver.execute_script(f"document.querySelector('[name=\"workDate\"]').value = '{work_date}'")
        driver.execute_script(f"document.querySelector('[name=\"startTime\"]').value = '{start_time}'")
        driver.execute_script(f"document.querySelector('[name=\"endTime\"]').value = '{end_time}'")

        # Submit the form
        driver.find_element(By.CSS_SELECTOR, "form").submit()

        # Wait until confirmation page loads
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        result_html = driver.page_source

    finally:
        driver.quit()

    return render_template('result.html', result=result_html)

if __name__ == '__main__':
    app.run(debug=True)
