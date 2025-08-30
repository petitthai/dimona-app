import requests

DIMONA_URL = "https://dimona.socialsecurity.be/dimona/unsecured/Step4SummaryFormAction.do"

def submit_dimona_form(payload):
    """
    Submit the Dimona form using POST and return the HTML/text result.
    payload: dictionary with the Dimona form fields
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        response = requests.post(DIMONA_URL, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error submitting Dimona form: {e}"
