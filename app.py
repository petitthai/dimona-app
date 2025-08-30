from flask import Flask, render_template, request
from dimona_client import submit_registration
from utils import get_yesterday_formatted

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        insz = request.form.get("insz")
        registration_type = request.form.get("registration_type")  # e.g., 'lunch' or 'dinner'

        # Use yesterday for testing
        date = get_yesterday_formatted()

        try:
            result_message = submit_registration(insz=insz, date=date, registration_type=registration_type)
            return render_template("result.html", success=True, message=result_message)
        except Exception as e:
            return render_template("result.html", success=False, message=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
