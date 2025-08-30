from flask import Flask, render_template, request
from dimona_client import submit_dimona_form
from utils import get_yesterday_formatted, build_dimona_payload
import config

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    date = get_yesterday_formatted()  # always yesterday for testing
    if request.method == "POST":
        start_time = request.form.get("start_time", "17:30")  # default dinner
        end_time = request.form.get("end_time", "21:30")
        
        payload = build_dimona_payload(
            employer_id=config.EMPLOYER_ID,
            insz=config.WORKER_INSS,
            date=date,
            start_time=start_time,
            end_time=end_time,
            registration_type="FLX"
        )
        
        result = submit_dimona_form(payload)
    
    return render_template("index.html", result=result, date=date)

if __name__ == "__main__":
    app.run(debug=True)
