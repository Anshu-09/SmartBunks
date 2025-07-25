from flask import Flask, render_template, request, send_file
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Path to default holiday file
DEFAULT_HOLIDAY_FILE = "default_holidays.xlsx"

def normalize_subject(subj):
    return subj.strip().lower()

def read_holidays(holiday_file):
    if holiday_file:
        holiday_df = pd.read_excel(holiday_file)
    else:
        holiday_df = pd.read_excel(DEFAULT_HOLIDAY_FILE)

    return set(holiday_df['Date'].dt.date)

def generate_schedule(form_data):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedule = {}
    for day in days:
        subjects = form_data.get(day)
        if subjects:
            subject_list = [normalize_subject(s) for s in subjects.split(',') if s.strip()]
            schedule[day] = subject_list
    return schedule

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        # Read schedule from form
        schedule = generate_schedule(request.form)

        # Read holidays
        holiday_file = request.files.get('holiday_file')
        holidays = read_holidays(holiday_file)

        # Initialize subject counts
        subject_count = {}
        current_date = start_date

        while current_date <= end_date:
            if current_date not in holidays:
                weekday = current_date.strftime('%A')
                subjects_today = schedule.get(weekday, [])
                for subj in subjects_today:
                    subject_count[subj] = subject_count.get(subj, 0) + 1
            current_date += timedelta(days=1)

        # Prepare result as DataFrame
        result_df = pd.DataFrame([
            {'Subject': subject.title(), 'Total Days': count}
            for subject, count in subject_count.items()
        ]).sort_values(by='Subject')

        return render_template('index.html', table=result_df.to_html(classes='table table-bordered table-striped', index=False), submitted=True)

    return render_template('index.html', submitted=False)

if __name__ == '__main__':
    app.run(debug=True)
