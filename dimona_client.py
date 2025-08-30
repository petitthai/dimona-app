import datetime

class DimonaClient:
    def __init__(self, employer_id):
        self.employer_id = employer_id

    def prepare_payload(self, inss, start_date, start_time, end_time, joint_commission="XXX", worker_type="FLX"):
        """
        Bereidt de payload voor Dimona-aanvraag voor.
        """
        payload = {
            "employerId": self.employer_id,
            "inss": inss,
            "startDate": start_date.strftime("%Y-%m-%d"),
            "startTime": start_time,
            "endDate": start_date.strftime("%Y-%m-%d"),
            "endTime": end_time,
            "jointCommission": joint_commission,
            "workerType": worker_type,
        }
        return payload

    def dummy_post(self, payload):
        """
        Voor testdoeleinden: print payload ipv echt posten.
        """
        print("Payload klaar om te posten:")
        for k, v in payload.items():
            print(f"{k}: {v}")

# Test
if __name__ == "__main__":
    client = DimonaClient(employer_id=100778056)
    payload = client.prepare_payload(
        inss="80080825973",
        start_date=datetime.date(2025, 8, 29),
        start_time="17:30",
        end_time="21:30"
    )
    client.dummy_post(payload)
