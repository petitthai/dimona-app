# dimona_client.py
import requests
from config import BASE_URL

def build_dimona_payload(worker_id, work_date, start_time, end_time):
    """
    Bouwt de payload voor het DIMONA formulier.
    """
    return {
        "selected_worker": worker_id,
        "work_date": work_date,
        "start_time": start_time,
        "end_time": end_time
    }

def submit_dimona_form(payload):
    """
    Simulated submission of Dimona form. 
    In test mode, returns a mock HTML page.
    """
    # For real use:
    # response = requests.post(BASE_URL, data=payload)
    # return response.text

    # Mock HTML for testing:
    return f"""
    <html>
    <body>
        <h2>Dimona resultaat voor werknemer {payload['selected_worker']}</h2>
        <p>Start: {payload['startingDate']} {payload['startingHour']}</p>
        <p>Einde: {payload['endingDate']} {payload['endingHour']}</p>
        <p>Employer ID: {payload['employerId']}</p>
    </body>
    </html>
    """
