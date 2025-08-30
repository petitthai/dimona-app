from datetime import datetime, timedelta

def get_yesterday_formatted():
    """
    Return yesterday's date in dd/mm/yyyy format.
    """
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%d/%m/%Y")

def parse_time_to_hhmm(time_str):
    """
    Convert time string like '12:00' or '17:30' to HHMM format for payload.
    """
    return time_str.replace(":", "")

def build_dimona_payload(employer_id, insz, date, start_time, end_time, registration_type):
    """
    Build the POST payload for the Dimona registration.
    """
    payload = {
        "buttonClicked": "confirm",
        "org.apache.struts.taglib.html.TOKEN": "dummy-token-for-testing",  # Replace or fetch dynamically
        "employerRef": "",
        "workerRef": "",
        "decRef0": "",
        "declarationNbr": "1",
        "loggedEntity": f"<LoggedEntity><noss>{employer_id}</noss></LoggedEntity>",
        "decXml0": f"""
            <DIMONA>
                <Form>
                    <Identification>DIMONA</Identification>
                    <FormCreationDate>{datetime.now().strftime('%Y-%m-%d')}</FormCreationDate>
                    <FormCreationHour>{datetime.now().strftime('%H:%M:%S')}</FormCreationHour>
                    <AttestationStatus>0</AttestationStatus>
                    <TypeForm>SU</TypeForm>
                    <DimonaIn>
                        <EmployerId>
                            <NOSSRegistrationNbr>{employer_id}</NOSSRegistrationNbr>
                        </EmployerId>
                        <NaturalPerson>
                            <INSS>{insz}</INSS>
                        </NaturalPerson>
                        <StartingDate>{datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')}</StartingDate>
                        <StartingHour>{parse_time_to_hhmm(start_time)}</StartingHour>
                        <EndingHour>{parse_time_to_hhmm(end_time)}</EndingHour>
                        <EndingDate>{datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')}</EndingDate>
                        <DimonaFeatures>
                            <WorkerType>FLX</WorkerType>
                        </DimonaFeatures>
                    </DimonaIn>
                </Form>
            </DIMONA>
        """,
        "previousPage": "",
        "workerBeanXml": f"<NaturalPerson><INSS>{insz}</INSS></NaturalPerson>",
        "PeriodList": f"[[DimonaPeriod nbr=0,in={datetime.strptime(date, '%d/%m/%Y').strftime('%Y%m%d')} {parse_time_to_hhmm(start_time)},out={datetime.strptime(date, '%d/%m/%Y').strftime('%Y%m%d')} {parse_time_to_hhmm(end_time)},type=[DimonaPeriodType jc=XXX,wc=FLX,user=null,se=null],canceled=false]]"
    }
    return payload
