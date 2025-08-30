import requests

DIMONA_URL = "https://dimona.socialsecurity.be/dimona/unsecured/Step4SummaryFormAction.do"

def submit_dimona_form(payload):
    # Verzend de payload naar DIMONA
    response = requests.post(DIMONA_URL, data=payload)
    response.raise_for_status()  # Fout als request niet lukt
    return response.text

def build_dimona_payload(worker_id, work_date, start_time=None, end_time=None):
    payload = {
        "selected_worker": worker_id,
        "work_date": work_date,  # gisteren
        "start_time": start_time or "09:00",
        "end_time": end_time or "17:00",
        # Voeg hier andere DIMONA verplichte velden toe:
        "employer_id": "100778056",
        # ...
    }
    return payload
