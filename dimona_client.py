import requests

DIMONA_URL = "https://dimona.socialsecurity.be/dimona/unsecured/Step4SummaryFormAction.do"

def submit_dimona_form(payload):
    response = requests.post(DIMONA_URL, data=payload)
    return response.text  # dit kunnen we in result.html tonen
