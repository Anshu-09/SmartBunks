from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def normalize(subject):
    return subject.strip().lower()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    # 1. Get date range and required attendance
    start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")
    required_attendance = int(request.form["required_attendance"])

    # 2. Get holiday file or use default
    holiday_file = request.files.get("holiday_file")
    if holiday_file and holiday_file.filename:
        holiday_path = os.path.join(UPLOAD_FOLDER, holiday_file.filename)
        holiday_file.save(holiday_path)
    else:
        holiday_path = "holiday.xlsx"  # default file

    holidays = pd.read_excel(holiday_path)["Date"].dt.date.tolist()

    # 3. Get timetable
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    timetable = {}
    for day in weekdays:
        subjects_input = request.form.getlist(f"{day}[]")
        if subjects_input:
            subjects = [normalize(sub) for sub in subjects_input[0].split(",") if sub.strip()]
            timetable[day] = subjects
        else:
            timetable[day] = []

    # 4. Calculate subject frequencies
    subject_counts = {}
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5 and current_date.date() not in holidays:
            day_name = weekdays[current_date.weekday()]
            subjects = timetable.get(day_name, [])
            for subject in subjects:
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
        current_date += timedelta(days=1)

    # 5. Generate recommendations
    results = []
    for subject, total_classes in subject_counts.items():
        allowed_bunks = total_classes - (total_classes * required_attendance // 100)
        results.append((subject.title(), total_classes, allowed_bunks))

    # 6. Create result table HTML
    df = pd.DataFrame(results, columns=["Subject", "Total Classes", "Bunks Allowed"])
    table_html = df.to_html(index=False, classes="result-table", border=0)

    return render_template("index.html", result=table_html)


if __name__ == "__main__":
    app.run(debug=True)
