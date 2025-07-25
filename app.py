from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None

    if request.method == 'POST':
        try:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            holiday_file = request.files.get('holiday_file')

            # Load default holiday file if none is uploaded
            if holiday_file and holiday_file.filename.endswith('.xlsx'):
                holiday_df = pd.read_excel(holiday_file)
            else:
                default_path = os.path.join('static', 'data', 'default_holidays.xlsx')
                holiday_df = pd.read_excel(default_path)

            # Count total working days
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            weekdays = date_range[date_range.dayofweek < 5]  # Monday to Friday

            # Remove holidays from working days
            holidays = pd.to_datetime(holiday_df['Date'], errors='coerce')
            working_days = [day for day in weekdays if day not in holidays]

            # Subject pattern based on weekdays (Mon–Fri)
            weekday_subjects = {
                0: "Math",       # Monday
                1: "Physics",    # Tuesday
                2: "Chemistry",  # Wednesday
                3: "English",    # Thursday
                4: "Computer"    # Friday
            }

            # Tally attendance by subject
            subject_counts = {}
            for day in working_days:
                subject = weekday_subjects.get(day.weekday())
                if subject:
                    # Normalize similar subject names
                    subject = subject.strip().lower()
                    subject = subject.replace("maths", "math")
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1

            # Convert keys back to title-case
            formatted_result = {subj.title(): count for subj, count in subject_counts.items()}
            result = formatted_result

        except Exception as e:
            error = f"An error occurred: {str(e)}"

    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
