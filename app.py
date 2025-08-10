from flask import Flask, render_template, request, send_from_directory,Request,redirect,session
import pandas as pd
import numpy as np
import os
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from sqlalchemy import select
app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class auth(db.Model):
    username=db.Column(db.String(300),primary_key=True)
    password_hash=db.Column(db.String(500),nullable=False)
    
    def __repr__(self):
        return f"<User {self.password_hash}>"

# Routes #
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "user_id" in session:
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
                "analyzer.html",
                result=result_html,
                auto_scroll=True,                # <== tells template to jump instantly
                start_date=start_date,
                end_date=end_date,
                threshold=threshold,
                **schedule_inputs,)
    else:
            return redirect("/login")
    

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


@app.route("/input",methods=["GET"])
def input():
    if "user_id" not in session:
        return redirect("/login")
    else:
        return render_template("input.html")


@app.route("/register",methods=["GET","POST"])
def register():
        if request.method=="POST":
            
            uid=request.form["username"]
            passwd=request.form["password"]
            
            passwd_bytes = passwd.encode('utf-8')
            
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(passwd_bytes, salt)

            myauth=auth(username=uid, password_hash=hashed.decode('utf-8'))
            db.session.add(myauth)
            db.session.commit()
            return redirect("/login")
        return render_template("register.html")


@app.route("/login",methods=["GET","POST"])
def login():
        if request.method=="POST":
            uid=request.form["username"]
            passwd=request.form["password"]
            user=db.session.execute(select(auth).where(auth.username==uid)).scalar_one_or_none()
            if user is None:
                return "User Not Found",404
            if bcrypt.checkpw(passwd.encode('utf-8'), user.password_hash.encode('utf-8')):
                session["user_id"] = user.username
                # session["username"] = user.username
                return redirect("/input")
            else:
                Wrong_Password_Alert="Wrong Password"
                return "Wrong Password",401
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
