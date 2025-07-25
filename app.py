from flask import Flask, render_template, request
import pandas as pd

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

            if not start_date or not end_date or not holiday_file:
                raise ValueError("All fields are required!")

            # Read holiday file
            holiday_df = pd.read_excel(holiday_file)
            holidays = pd.to_datetime(holiday_df['Date'], errors='coerce')

            # Calculate working weekdays excluding holidays
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            weekdays = date_range[date_range.dayofweek < 5]
            working_days = [day for day in weekdays if day not in holidays]

            # Subject map by weekday
            weekday_subjects = {
                0: "Math",
                1: "Physics",
                2: "Chemistry",
                3: "English",
                4: "Computer"
            }

            # Count subjects
            subject_counts = {}
            for day in working_days:
                subject = weekday_subjects.get(day.weekday())
                if subject:
                    subject = subject.strip().lower()
                    subject = subject.replace("maths", "math")
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1

            result = {k.title(): v for k, v in subject_counts.items()}

        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
