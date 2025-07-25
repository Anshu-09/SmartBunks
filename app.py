from flask import Flask, render_template, request
import pandas as pd
from fuzzywuzzy import fuzz
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def normalize_subjects(subjects, threshold=85):
    """Automatically merge similar subject names using fuzzy matching."""
    unique_subjects = []
    subject_map = {}

    for subject in subjects:
        subject_clean = subject.strip().lower()
        matched = False

        for ref in unique_subjects:
            if fuzz.ratio(subject_clean, ref) >= threshold:
                subject_map[subject] = ref
                matched = True
                break

        if not matched:
            unique_subjects.append(subject_clean)
            subject_map[subject] = subject_clean

    return subject_map

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if 'scheduleFile' not in request.files or 'holidaysFile' not in request.files:
        return "Missing file(s)", 400

    schedule_file = request.files['scheduleFile']
    holidays_file = request.files['holidaysFile']
    start_date = request.form['startDate']
    end_date = request.form['endDate']

    if not schedule_file or not holidays_file or schedule_file.filename == '' or holidays_file.filename == '':
        return "No selected file", 400

    # Save and load files
    schedule_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(schedule_file.filename))
    holidays_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(holidays_file.filename))
    schedule_file.save(schedule_path)
    holidays_file.save(holidays_path)

    df = pd.read_excel(schedule_path)
    holidays = pd.read_excel(holidays_path)

    df['Date'] = pd.to_datetime(df['Date'])
    holidays['Date'] = pd.to_datetime(holidays['Date'])

    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    df = df[~df['Date'].isin(holidays['Date'])]

    # Normalize subjects
    subject_map = normalize_subjects(df['Subject'].tolist())
    df['Subject'] = df['Subject'].map(subject_map)

    grouped = df.groupby('Subject').size().reset_index(name='TotalClasses')
    grouped['MinRequired'] = (grouped['TotalClasses'] * 0.75).apply(lambda x: int(x) if x.is_integer() else int(x) + 1)
    grouped['MaxAbsents'] = grouped['TotalClasses'] - grouped['MinRequired']
    grouped['Subject'] = grouped['Subject'].str.title()

    return render_template('result.html', tables=grouped.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
