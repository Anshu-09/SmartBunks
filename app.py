from flask import Flask, request, render_template, send_file
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Get uploaded files and date inputs
    schedule_file = request.files['schedule']
    holidays_file = request.files['holidays']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # Save uploaded files
    schedule_path = os.path.join(UPLOAD_FOLDER, 'schedule.xlsx')
    holidays_path = os.path.join(UPLOAD_FOLDER, 'holidays.xlsx')
    schedule_file.save(schedule_path)
    holidays_file.save(holidays_path)

    # === LOAD DATA ===
    schedule_df = pd.read_excel(schedule_path, index_col=0)
    holidays_df = pd.read_excel(holidays_path)

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
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }

    subject_weekday_count = {}
    for day, row in schedule_df.iterrows():
        for subject in row:
            subject = str(subject).strip()
            if subject == '' or subject.lower() == 'nan':
                continue
            if subject not in subject_weekday_count:
                subject_weekday_count[subject] = {}
            if day not in subject_weekday_count[subject]:
                subject_weekday_count[subject][day] = 0
            subject_weekday_count[subject][day] += 1

    subject_attendance_data = []
    for subject, days in subject_weekday_count.items():
        total_classes = 0
        for day, count in days.items():
            classes = count * effective_weekdays.get(day, 0)
            total_classes += classes
        min_required = int(np.ceil(total_classes * 0.75))
        max_absents = total_classes - min_required
        subject_attendance_data.append({
            'Subject': subject,
            'TotalClasses': total_classes,
            'MinRequired': min_required,
            'MaxAbsents': max_absents
        })

    result_df = pd.DataFrame(subject_attendance_data)
    output_path = os.path.join(UPLOAD_FOLDER, 'attendance_analysis.xlsx')
    result_df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
