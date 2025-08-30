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
    Stuur de DIMONA gegevens door.
    Voor test doeleinden geven we hier gewoon een string terug.
    """
    worker = payload.get("selected_worker", "Onbekend")
    return f"<h2>Dimona resultaat voor werknemer {worker}</h2>" \
           f"<p>Datum: {payload.get('work_date')}</p>" \
           f"<p>Van {payload.get('start_time')} tot {payload.get('end_time')}</p>"
