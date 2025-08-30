import requests
from utils import build_dimona_payload, get_yesterday_formatted
from config import EMPLOYER_ID

DIMONA_URL = "https://dimona.socialsecurity.be/dimona/unsecured/Step4SummaryFormAction.do"

def submit_registration(insz: str, registration_type: str):
    """
    Submit a Dimona registration for testing using yesterday's date.
    
    :param insz: The worker's INSZ/SSN
    :param registration_type: 'lunch' or 'dinner'
    :return: Result message from the registration attempt
    """
    # Use yesterday for testing
    date = get_yesterday_formatted()

    # Determine start and end times based on registration type
    if registration_type.lower() == "lunch":
        start_time = "12:00"
        end_time = "14:00"
    elif registration_type.lower() == "dinner":
        start_time = "17:30"
        end_time = "21:30"
    else:
        raise ValueError("Invalid registration type. Choose 'lunch' or 'dinner'.")

    # Build payload for the final step
    payload = build_dimona_payload(
        employer_id=EMPLOYER_ID,
        insz=insz,
        date=date,
        start_time=start_time,
        end_time=end_time,
        registration_type=registration_type
    )

    # Perform POST request to Dimona
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "DimonaTestApp/1.0"
    }

    response = requests.post(DIMONA_URL, data=payload, headers=headers, timeout=15)

    if response.status_code == 200:
        # You could parse HTML or return raw content
        return "Registration submitted successfully (test date: {})".format(date)
    else:
        raise Exception(f"Dimona registration failed with status {response.status_code}")
