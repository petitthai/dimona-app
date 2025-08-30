# backend/config.py

# Employer info
EMPLOYER_ID = "100778056"
NOSS_NUMBER = "101380519"
COMPANY_ID = "766985433"
COMPANY_NAME = "PETIT THAI BV"

# Testmode: als True gebruikt het gisteren als datum
TEST_MODE = True

# Dimona endpoints
DIMONA_BASE_URL = "https://dimona.socialsecurity.be/dimona/unsecured/"
STEP1_URL = f"{DIMONA_BASE_URL}Step1FormAction.do"
STEP2_URL = f"{DIMONA_BASE_URL}Step2FormAction.do"
STEP3_URL = f"{DIMONA_BASE_URL}Step3FormAction.do"
STEP4_URL = f"{DIMONA_BASE_URL}Step4SummaryFormAction.do"

# Default times
LUNCH_START = "12:00"
LUNCH_END = "14:00"
DINNER_START = "17:30"
DINNER_END = "21:30"
