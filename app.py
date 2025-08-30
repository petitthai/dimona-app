# app.py
from flask import Flask, render_template
import config
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # Voor test: toon employer ID en huidige datum/tijd
    return f"Employer ID: {config.EMPLOYER_ID} | Tijd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

if __name__ == '__main__':
    app.run(debug=True)
