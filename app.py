from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import numpy as np
import os

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_attendance():
    try:
        # === GET DATES FROM FORM ===
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date are required.'}), 400

        # === GET FILES ===
        schedule_file = request.files.get('schedule')
        holidays_file = request.files.get('holidays')

        if not schedule_file or not holidays_file:
            return jsonify({'error': 'Both schedule and holidays files are required.'}), 400

        # === READ EXCEL FILES ===
        schedule_df = pd.read_excel(schedule_file, index_col=0)
        holidays_df = pd.read_excel(holidays_file)
        holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])

        # === FILTER HOLIDAYS IN DATE RANGE ===
        holidays_df = holidays_df[
            (holidays_df['Date'] >= pd.to_datetime(start_date)) &
            (holidays_df['Date'] <= pd.to_datetime(end_date))
        ]
        holidays_df['Weekday'] = holidays_df['Date'].dt.day_name()

        # === HOLIDAY WEEKDAY COUNTS ===
        weekday_holiday_count = holidays_df['Weekday'].value_counts().to_dict()

        # === ALL WEEKDAYS IN RANGE ===
        all_dates = pd.date_range(start=start_date, end=end_date)
        weekday_counts = pd.Series([d.strftime('%A') for d in all_dates]).value_counts().to_dict()

        effective_weekdays = {
            day: max(0, weekday_counts.get(day, 0) - weekday_holiday_count.get(day, 0))
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        }

        # === SUBJECT WEEKDAY OCCURRENCE COUNT ===
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

        # === FINAL ANALYSIS ===
        ATTENDANCE_THRESHOLD = 0.75
        subject_attendance_data = []
        for subject, days in subject_weekday_count.items():
            total_classes = 0
            for day, count in days.items():
                classes = count * effective_weekdays.get(day, 0)
                total_classes += classes
            min_required = int(np.ceil(total_classes * ATTENDANCE_THRESHOLD))
            max_absents = total_classes - min_required
            subject_attendance_data.append({
                'Subject': subject,
                'TotalClasses': total_classes,
                'MinRequired': min_required,
                'MaxAbsents': max_absents
            })

        result_df = pd.DataFrame(subject_attendance_data)

        # Save and optionally return file
        output_path = os.path.join(os.getcwd(), "attendance_analysis.xlsx")
        result_df.to_excel(output_path, index=False)

        return result_df.to_json(orient="records")

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
