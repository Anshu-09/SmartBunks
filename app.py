from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', result=None)

@app.route('/upload', methods=['POST'])
def upload_files():
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # Read schedule from form input instead of Excel
    schedule_df = {}
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        subjects_str = request.form.get(f'schedule_{day}', '')
        subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]
        schedule_df[day] = subjects

    holidays_file = request.files['holidays']

    # Load dataframes
    holidays_df = pd.read_excel(holidays_file)

    # Convert and filter holidays
    holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
    holidays_df = holidays_df[
        (holidays_df['Date'] >= pd.to_datetime(start_date)) &
        (holidays_df['Date'] <= pd.to_datetime(end_date))
    ]
    holidays_df['Weekday'] = holidays_df['Date'].dt.day_name()

    # Count holidays by weekday
    weekday_holiday_count = holidays_df['Weekday'].value_counts().to_dict()

    # Count all weekdays in date range
    all_dates = pd.date_range(start=start_date, end=end_date)
    weekday_counts = pd.Series([d.strftime('%A') for d in all_dates]).value_counts().to_dict()

    # Calculate effective weekdays
    effective_weekdays = {
        day: max(0, weekday_counts.get(day, 0) - weekday_holiday_count.get(day, 0))
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday']
    }

    # Count subject occurrences per weekday
    subject_weekday_count = {}
    for day, subjects in schedule_df.items():
        for subject in subjects:
            if subject.lower() == 'nan' or subject == '':
                continue
            if subject not in subject_weekday_count:
                subject_weekday_count[subject] = {}
            if day not in subject_weekday_count[subject]:
                subject_weekday_count[subject][day] = 0
            subject_weekday_count[subject][day] += 1

    # Calculate attendance info
    threshold_percent = float(request.form['threshold'])  # e.g., 75
    ATTENDANCE_THRESHOLD = threshold_percent / 100.0

    subject_attendance_data = []
    for subject, days in subject_weekday_count.items():
        total_classes = 0
        for day, count in days.items():
            total_classes += count * effective_weekdays.get(day, 0)
        min_required = int(np.ceil(total_classes * ATTENDANCE_THRESHOLD))
        max_absents = total_classes - min_required
        subject_attendance_data.append({
            'Subject': subject,
            'TotalClasses': total_classes,
            'MinRequired': min_required,
            'MaxAbsents': max_absents
        })

    # Convert to DataFrame for HTML rendering
    result_df = pd.DataFrame(subject_attendance_data)

    # Convert DataFrame to HTML table
    result_html = result_df.to_html(classes='table table-bordered table-striped', index=False)

    return render_template('index.html', result=result_html)

if __name__ == '__main__':
    app.run(debug=True)
