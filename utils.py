# utils.py
from datetime import datetime, timedelta

def get_yesterday_formatted():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def parse_time_to_hhmm(time_str):
    """Convert '17:30' -> '1730'"""
    return time_str.replace(":", "")

def build_dimona_payload(worker_id, work_date=None, start_time=None, end_time=None):
    payload = {
        "selected_worker": worker_id,   # <-- dit is nodig voor dimona_client.py
        "work_date": work_date,
        "start_time": start_time,
        "end_time": end_time
    }
    return payload
