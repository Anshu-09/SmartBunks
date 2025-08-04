from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# ------------------------------------------------------------------ #
# Routes #
@app.route("/", methods=["GET"])
def index():
    """Landing page or refreshed page with no result."""
    return render_template("index.html", result=None, auto_scroll=False)

@app.route("/upload", methods=["POST"])
def upload_files():
    #Read form data ------------------------------------------------
    start_date  = request.form.get("start_date")
    end_date    = request.form.get("end_date")
    threshold   = float(request.form.get("threshold", 75))

    # Weekly schedule -------------------------------------------------------------
    schedule_inputs = {}
    schedule_df = {}
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
        key = f"schedule_{day}"
        subjects_str = request.form.get(key, "")
        schedule_inputs[key] = subjects_str                       # keep for re‑fill
        schedule_df[day] = [
            s.strip().upper() for s in subjects_str.split(",") if s.strip()
        ]

    #Holiday file (user or default) -------------------------------
    holidays_file = request.files.get("holidays")
    if holidays_file and holidays_file.filename:
        holidays_df = pd.read_excel(holidays_file)
    else:
        default_path = os.path.join("static", "data", "holidays.xlsx")
        holidays_df = pd.read_excel(default_path)

    # Holiday + calendar maths ------------------------------------
    holidays_df["Date"] = pd.to_datetime(holidays_df["Date"])
    holidays_df = holidays_df[
        (holidays_df["Date"] >= pd.to_datetime(start_date))
        & (holidays_df["Date"] <= pd.to_datetime(end_date))
    ]
    holidays_df["Weekday"] = holidays_df["Date"].dt.day_name()
    weekday_holiday_cnt = holidays_df["Weekday"].value_counts().to_dict()

    all_dates = pd.date_range(start=start_date, end=end_date)
    weekday_total_cnt = pd.Series(d.strftime("%A") for d in all_dates).value_counts().to_dict()

    effective_weekdays = {
        day: max(0, weekday_total_cnt.get(day, 0) - weekday_holiday_cnt.get(day, 0))
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    }

    # - 4.  Subject attendance maths
    subject_weekday_cnt = {}
    for day, subjects in schedule_df.items():
        for sbj in subjects:
            if not sbj:
                continue
            subject_weekday_cnt.setdefault(sbj, {}).setdefault(day, 0)
            subject_weekday_cnt[sbj][day] += 1

    ATT_THRESH = threshold / 100.0
    rows = []
    for sbj, day_map in subject_weekday_cnt.items():
        total = sum(cnt * effective_weekdays.get(day, 0) for day, cnt in day_map.items())
        min_req = int(np.ceil(total * ATT_THRESH))
        rows.append(
            dict(Subject=sbj, TotalClasses=total, DaysToAttend=min_req, AbsentsAllowed=total - min_req)
        )

    result_html = (
        pd.DataFrame(rows)
        .sort_values("Subject")
        .to_html(classes="table table-bordered table-striped",index=False)
    )

    #-- 5.  Render same page, but flag auto_scroll=True --
    return render_template(
        "index.html",
        result=result_html,
        auto_scroll=True,                # <== tells template to jump instantly
        start_date=start_date,
        end_date=end_date,
        threshold=threshold,
        **schedule_inputs,
    )

@app.route("/download-default-holidays")
def download_holiday_format():
    return send_from_directory(
        directory=os.path.join(app.root_path, "static", "data"),
        path="holidays.xlsx",
        as_attachment=True,
    )
@app.route("/download-default-kiit-holidays")
def download_kiit_holiday_format():
    return send_from_directory(
        directory=os.path.join(app.root_path, "static", "data"),
        path="kiit-holidays.xlsx",
        as_attachment=True,
    )


if __name__ == "__main__":
    app.run(debug=True)
