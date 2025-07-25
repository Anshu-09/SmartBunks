from flask import Flask, request, jsonify, render_template
import pandas as pd
import io
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET'])

def index():
    return render_template('index.html')  # Load the upload form
=======
def home():
    return "✅ SmartBunks Flask app is running!"

@app.route('/', methods=['POST'])
def analyze_attendance():
    try:
        # Parse dates
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Start and end dates are required'}), 400

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if start_date > end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400

        # Read uploaded files
        schedule_file = request.files.get('schedule')
        holidays_file = request.files.get('holidays')

        if not schedule_file or not holidays_file:
            return jsonify({'error': 'Both schedule and holidays files are required'}), 400

        schedule_df = pd.read_excel(schedule_file)
        holidays_df = pd.read_excel(holidays_file)

        # Convert holiday dates to set for fast lookup
        holidays_set = set(pd.to_datetime(holidays_df.iloc[:, 0]).dt.date)

        # Analyze attendance
        result = []

        for index, row in schedule_df.iterrows():
            name = row['Name']
            section = row['Section']
            attended_dates = pd.to_datetime(row[2:].dropna()).dt.date.tolist()

            total_lectures = 0
            lectures_attended = 0

            current_date = start_date
            while current_date <= end_date:
                if current_date not in holidays_set:
                    total_lectures += 1
                    if current_date in attended_dates:
                        lectures_attended += 1
                current_date += timedelta(days=1)

            attendance_percentage = (lectures_attended / total_lectures) * 100 if total_lectures > 0 else 0

            result.append({
                'Name': name,
                'Section': section,
                'Total Lectures': total_lectures,
                'Lectures Attended': lectures_attended,
                'Attendance %': round(attendance_percentage, 2)
            })

        return jsonify({'status': 'success', 'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
