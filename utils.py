from datetime import datetime, timedelta

def get_yesterday_formatted():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%d/%m/%Y")

def build_dimona_payload(worker_id, date):
    payload = {
        "worker_id": worker_id,
        "dateFlexi": date,
        "buttonClicked": "confirm",
        # Voeg hier je andere vaste velden toe of laad uit config
    }
    return payload
