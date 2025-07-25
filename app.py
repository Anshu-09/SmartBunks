from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ SmartBunks Flask app is running!'

@app.route('/analyze', methods=['POST'])
def analyze_attendance():
    try:
        # Check uploaded files
        if 'schedule' not in request.files or 'holidays' not in request.files:
            return jsonify({"error": "Missing schedule or holidays file"}), 400

        schedule_file = request.files['schedule']
        holidays_file = request.files['holidays']

        # Save files to disk temporarily
        schedule_file.save("schedule.xlsx")
        holidays_file.save("holidays.xlsx")

        # === LOGIC STARTS ===
        print("Current working directory:", os.getcwd())

        START_DATE = '2025-07-11'
        END_DATE = '2025-09-05'
        ATTENDANCE_THRESHOLD = 0.75

        # Load data
        schedule_df = pd.read_excel("schedule.xlsx", index_col=0)
        holidays_df = pd.read_excel("holidays.xlsx")

        # Process holidays
        holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
        holidays_df = holidays_df[
            (holidays_df['Date'] >= pd.to_datetime(START_DATE)) &
            (holidays_df['Date'] <= pd.to_datetime(END_DATE))
        ]
        holidays_df['Weekday'] = holidays_df['Date'].dt.day_name()

        # Weekday counts
        weekday_holiday_count = holidays_df['Weekday'].value_counts().to_dict()
        all_dates = pd.date_range(start=START_DATE, end=END_DATE)
        weekday_counts = pd.Series([d.strftime('%A') for d in all_dates]).value_counts().to_dict()

        # Effective weekdays
        effective_weekdays = {
            day: max(0, weekday_counts.get(day, 0) - weekday_holiday_count.get(day, 0))
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        }

        # Subject weekday count
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

        # Attendance logic
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

        # Final result
        result_df = pd.DataFrame(subject_attendance_data)
        result_df.to_excel("attendance_analysis.xlsx", index=False)

        return result_df.to_json(orient='records'), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
