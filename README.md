
# 🎓 SmartBunks – Smart Attendance Calculator

* SmartBunks** is a Flask-powered attendance analyzer that helps students calculate how many classes they can safely skip (aka *bunk*) while staying within the minimum required attendance percentage (default: 75%).

---

## ✨ Features

- 📅 Upload your weekly class schedule (Excel)
- 📌 Add a list of semester holidays (Excel)
- 🕓 Enter your semester start and end dates
- ✅ Get total classes, required attendance, and allowed absents per subject
- 📥 Download the output Excel report

---

## 📁 Input File Formats

### 1. `schedule.xlsx`

A weekly class schedule. Each cell represents the subject for a slot.

|        | Monday | Tuesday | Wednesday | Thursday | Friday |
|--------|--------|---------|-----------|----------|--------|
| Slot 1 | Maths  | Chem    | Phys      | ...      | ...    |
| Slot 2 | ...    | ...     | ...       | ...      | ...    |

> Empty cells mean no class for that slot.

### 2. `holidays.xlsx`

| Date       |
|------------|
| 2025-08-15 |
| 2025-08-28 |
| ...        |

- Format: `YYYY-MM-DD`
- List holidays that fall within the semester duration

---

## 🧠 Logic Behind the App

- Calculates how many weekdays exist between the semester start and end dates.
- Subtracts holidays that fall on those weekdays.
- Multiplies with subject frequency per weekday.
- Computes:
  - ✅ **Total Classes**
  - 📉 **Minimum Required (75%)**
  - 🚫 **Max Allowable Absents**

---

## 🚀 How to Run Locally

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername SmartBunks.git
cd SmartBunks
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install flask pandas openpyxl numpy
```

### 3. Run the App

```bash
python app.py
```

The server runs at: `http://localhost:5000`

---

## 📬 Using Postman or Frontend

### Endpoint: `POST /analyze`

**URL**: `http://localhost:5000/analyze`  
**Body Type**: `form-data`

| Key         | Type     | Description                        |
|-------------|----------|------------------------------------|
| schedule    | File     | Upload your `schedule.xlsx`        |
| holidays    | File     | Upload your `holidays.xlsx`        |
| start_date  | Text     | Format: `YYYY-MM-DD`               |
| end_date    | Text     | Format: `YYYY-MM-DD`               |

**Response**: Downloadable Excel file containing your attendance analysis.

---

## 📤 Deployment (Free Hosting Options)

You can deploy SmartBunks online using:

- **Render**: Best for Flask with auto-redeploy
- **Railway**: Easy GitHub integration
- **Replit**: Good for quick demos
- **Fly.io** or **Vercel (w/ adapter)**

### Quick Deploy with Render:

1. Push this code to GitHub
2. Go to [https://render.com](https://render.com)
3. Click **"New Web Service"**
4. Connect your GitHub, choose this repo
5. Set Build Command: `pip install -r requirements.txt`
6. Start Command: `python app.py`
7. Done! Share your hosted link 🎉

---

## 📦 Output

The output is an Excel file like this:

| Subject | TotalClasses | MinRequired | MaxAbsents |
|---------|--------------|-------------|------------|
| Maths   | 32           | 24          | 8          |
| Chem    | 30           | 22          | 8          |
| ...     | ...          | ...         | ...        |

---

## 🔒 License

MIT License — feel free to use, modify, and contribute!

---

## 🤝 Contributing

Pull requests and suggestions are welcome!  
If you'd like to add GUI, login system, or database support — feel free to fork and build.

---

## 💡 Idea Behind SmartBunks

This project was born from a student's need to quickly calculate their attendance limits without manually checking calendars and timetables. It automates what every student has thought at least once:

> "How many classes can I bunk without falling below 75%?"

---

## 🔗 Connect

If you use or extend SmartBunks, give it a ⭐ and tag the repo on socials!
