import os
from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder to store uploaded files temporarily
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for homepage and form submission
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        schedule_file = request.files["schedule_file"]
        holiday_file = request.files.get("holiday_file")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        target_percentage = float(request.form.get("target_percentage", 75))

        # Save schedule file
        schedule_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(schedule_file.filename))
        schedule_file.save(schedule_path)

        # Use uploaded holiday file or default one
        if holiday_file and holiday_file.filename != "":
            holiday_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(holiday_file.filename))
            holiday_file.save(holiday_path)
        else:
            holiday_path = os.path.join("static", "data", "holiday.xlsx")

        # Read Excel files
        try:
            schedule_df = pd.read_excel(schedule_path)
            holiday_df = pd.read_excel(holiday_path)
        except Exception as e:
            return f"Error reading files: {e}"

        # Parse timetable data from form
        timetable = {}
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            subjects = request.form.get(day, "")
            subject_list = [sub.strip() for sub in subjects.split(",") if sub.strip()]
            timetable[day.capitalize()] = subject_list

        # Convert date strings to datetime objects
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Generate list of all weekdays between start and end
        date_range = pd.date_range(start=start, end=end)
        holidays = set(pd.to_datetime(holiday_df["Date"]).dt.date)

        # Create attendance calculation
        records = []
        subject_counts = {}

        for date in date_range:
            day_name = date.strftime("%A")
            if day_name in timetable and date.date() not in holidays:
                subjects_today = timetable[day_name]
                for sub in subjects_today:
                    subject_counts[sub] = subject_counts.get(sub, 0) + 1

        # Total classes possible per subject
        report = []
        for subject, total_classes in subject_counts.items():
            required = int((target_percentage / 100) * total_classes)
            report.append({
                "Subject": subject,
                "Total Classes": total_classes,
                "Required for Target %": required
            })

        report_df = pd.DataFrame(report)
        report_df = report_df.sort_values(by="Subject")

        return render_template("index.html", tables=report_df.to_html(classes="table-auto w-full text-sm text-left text-gray-700 border", index=False, border=0))

    return render_template("index.html", tables=None)

if __name__ == "__main__":
    app.run(debug=True)
