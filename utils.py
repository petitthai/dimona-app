# utils.py
from datetime import datetime, timedelta

def get_yesterday_formatted():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def parse_time_to_hhmm(time_str):
    """Convert '17:30' -> '1730'"""
    return time_str.replace(":", "")

def build_dimona_payload(worker_id, start_hour="1700", end_hour="2100"):
    """Return a payload dictionary for Dimona submission."""
    date = get_yesterday_formatted()
    return {
        "selected_worker": worker_id,
        "startingDate": date,
        "startingHour": start_hour,
        "endingHour": end_hour,
        "endingDate": date,
        "employerId": config.EMPLOYER_ID
    }
