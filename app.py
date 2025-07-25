from flask import Flask, render_template, request
import pandas as pd
import os
from werkzeug.utils import secure_filename
from collections import defaultdict

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DEFAULT_HOLIDAY_FILE = 'static/default_holidays.xlsx'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    start_date = pd.to_datetime(request.form['start_date'])
    end_date = pd.to_datetime(request.form['end_date'])

    # Load holiday file (user uploaded or default)
    holiday_file = request.files.get('holiday_file')
    if holiday_file and holiday_file.filename.endswith('.xlsx'):
        filename = secure_filename(holiday_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        holiday_file.save(filepath)
        holidays = pd.read_excel(filepath)['Date'].dt.date.tolist()
    else:
        holidays = pd.read_excel(DEFAULT_HOLIDAY_FILE)['Date'].dt.date.tolist()

    # Get subject schedule from form
    schedule = {}
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        subjects = request.form.get(day, "")
        schedule[day] = [s.strip().lower() for s in subjects.split(",") if s.strip()]

    # Generate date range and attendance counts
    all_dates = pd.date_range(start=start_date, end=end_date)
    attendance = defaultdict(lambda: {"Total": 0, "Present": 0})

    for date in all_dates:
        if date.date() in holidays or date.strftime('%A') not in schedule:
            continue
        weekday = date.strftime('%A')
        for subject in schedule[weekday]:
            attendance[subject]["Total"] += 1
            attendance[subject]["Present"] += 1  # Default assuming 100% present for now

    # Create result table
    df_result = pd.DataFrame([
        {"Subject": subj.title(), "Total Classes": data["Total"], "Present": data["Present"], "Attendance (%)": round((data["Present"] / data["Total"] * 100) if data["Total"] > 0 else 0, 2)}
        for subj, data in attendance.items()
    ])

    tables = [df_result.to_html(classes='table table-bordered table-hover mt-4', index=False)]

    return render_template('index.html', tables=tables)

if __name__ == '__main__':
    app.run(debug=True)
