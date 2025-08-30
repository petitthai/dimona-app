# utils.py
from datetime import datetime

def format_date_ddmmyyyy(date_obj):
    """
    Converts a datetime.date or datetime.datetime object to a string in dd/mm/yyyy format.
    """
    return date_obj.strftime("%d/%m/%Y")

def get_today_formatted():
    """
    Returns today's date in dd/mm/yyyy format.
    """
    return format_date_ddmmyyyy(datetime.today())

def get_yesterday_formatted():
    """
    Returns yesterday's date in dd/mm/yyyy format.
    """
    yesterday = datetime.today() - timedelta(days=1)
    return format_date_ddmmyyyy(yesterday)

def parse_time_to_hhmm(time_str):
    """
    Converts a string like '17:30' to a standardized hhmm string '1730'.
    """
    return time_str.replace(":", "")

def build_dimona_payload(employer_id, inss, start_date, start_hour, end_hour, commission, worker_type):
    """
    Builds the Dimona XML payload for submission.
    """
    payload_template = f"""
    <DIMONA>
        <Form>
            <Identification>DIMONA</Identification>
            <DimonaIn>
                <EmployerId>
                    <NOSSRegistrationNbr>{employer_id}</NOSSRegistrationNbr>
                </EmployerId>
                <NaturalPerson>
                    <INSS>{inss}</INSS>
                </NaturalPerson>
                <StartingDate>{start_date}</StartingDate>
                <StartingHour>{start_hour}</StartingHour>
                <EndingHour>{end_hour}</EndingHour>
                <DimonaFeatures>
                    <JointCommissionNbr>{commission}</JointCommissionNbr>
                    <WorkerType>{worker_type}</WorkerType>
                </DimonaFeatures>
            </DimonaIn>
        </Form>
    </DIMONA>
    """
    return payload_template.strip()
