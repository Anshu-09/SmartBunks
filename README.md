# SmartBunks (Render Version)

SmartBunks is an intelligent attendance calculator built with Flask. It allows users to upload their weekly schedule and optional holiday list to analyze attendance and determine how many classes they can bunk without falling below a given threshold.

---

## 🚀 Features

- Upload weekly subject schedule (Monday to Sunday)
- Upload optional holiday Excel file
- Set attendance threshold (e.g. 75%)
- Auto-calculate the number of classes you can safely bunk
- Returns a subject-wise attendance analysis
- Hosted on **Render**

---

## 🗂️ Folder Structure

```
SmartBunks/
├── static/
│   └── data/
│       └── holidays.xlsx        # Default holidays fallback file
├── templates/
│   └── index.html               # Frontend form and display
├── uploads/                     # Stores uploaded holiday files
├── app.py                       # Flask backend logic
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🧪 Local Testing Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/SmartBunks.git
cd SmartBunks
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate       # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask App

```bash
python app.py
```

Flask will run locally on:  
👉 `http://127.0.0.1:5000/`

---

## 📤 Deployment (Render)

This project is already deployed on [smartbunks.onrender.com](https://smartbunks.onrender.com/)

---

## 📁 Input Format

### Weekly Schedule
Paste subject names for each weekday in separate textareas (comma-separated).

Example for Monday:
```
Maths,Physics,Chemistry
```

### Holiday File
Upload an `.xlsx` file with a single column of dates (formatted as `DD-MM-YYYY`).

If you don't upload, default holidays from `static/data/holidays.xlsx` are used.

---

## 📊 Output

After submitting, you'll get a table showing:

- Total classes per subject
- Required classes (based on threshold)
- Maximum bunkable classes

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
