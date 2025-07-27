# Updated app.py

from flask import Flask, render_template, request, send_from_directory
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
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    threshold = request.form.get('threshold', 75)

    schedule_inputs = {}
    schedule_df = {}
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
        key = f'schedule_{day}'
        subjects_str = request.form.get(key, '')
        schedule_inputs[key] = subjects_str
        subjects = [s.strip().upper() for s in subjects_str.split(',') if s.strip()]
        schedule_df[day] = subjects

    # Load holidays
    holidays_file = request.files.get('holidays')
    if holidays_file and holidays_file.filename != '':
        holidays_df = pd.read_excel(holidays_file)
    else:
        default_path = os.path.join('static', 'data', 'holidays.xlsx')
        holidays_df = pd.read_excel(default_path)

    holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
    holidays_df = holidays_df[
        (holidays_df['Date'] >= pd.to_datetime(start_date)) &
        (holidays_df['Date'] <= pd.to_datetime(end_date))
    ]
    holidays_df['Weekday'] = holidays_df['Date'].dt.day_name()
    weekday_holiday_count = holidays_df['Weekday'].value_counts().to_dict()

    all_dates = pd.date_range(start=start_date, end=end_date)
    weekday_counts = pd.Series([d.strftime('%A') for d in all_dates]).value_counts().to_dict()

    effective_weekdays = {
        day: max(0, weekday_counts.get(day, 0) - weekday_holiday_count.get(day, 0))
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    }

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

    ATTENDANCE_THRESHOLD = float(threshold) / 100.0
    subject_attendance_data = []
    for subject, days in subject_weekday_count.items():
        total_classes = sum(count * effective_weekdays.get(day, 0) for day, count in days.items())
        min_required = int(np.ceil(total_classes * ATTENDANCE_THRESHOLD))
        max_absents = total_classes - min_required
        subject_attendance_data.append({
            'Subject': subject,
            'TotalClasses': total_classes,
            'MinRequired': min_required,
            'MaxAbsents': max_absents
        })

    result_df = pd.DataFrame(subject_attendance_data)
    result_html = result_df.to_html(classes='table table-bordered table-striped', index=False)

    return render_template(
        'index.html',
        result=result_html,
        start_date=start_date,
        end_date=end_date,
        threshold=threshold,
        **schedule_inputs
    )

@app.route('/download-default-holidays')
def download_holiday_format():
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static', 'data'),
        path='holidays.xlsx',
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
