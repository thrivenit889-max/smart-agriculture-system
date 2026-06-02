# Smart Agriculture & Rural Tech Web Application

A modern, responsive, and secure Web Application built using Python Flask, SQLite, HTML5, CSS3, JavaScript, and Bootstrap 5. It integrates browser-side AI classification models (TensorFlow.js & MobileNet v2) for crop leaf disease diagnostics and pest identification, natural language voice analysis for Kannada & English speech commands, telemetry charts, cash-flow ledger managers, and print-ready automated performance reporting layouts.

---

## 🌟 Key Features

1. **User Auth & Role Management**: Secure registration & login for Farmers with PBKDF2 cryptography. Includes administrative role structures.
2. **Interactive Weather Forecast**: Multi-metric weather cards (Wind, Rain, Humidity) with 7-day outlook feeds and agricultural hazard alert warnings.
3. **AI Soil Analysis & Crop suggestions**: Enter soil parameters (pH, N, P, K, Organic Matter) and upload report documents. Computes nutrient balance health scores and matches ideal crops.
4. **Targeted Fertilizer Calculator**: Computes target shortfalls in kg/acre and schedules 3-split fertilizer applications (Urea, SSP, MOP).
5. **Smart Irrigation Telemetry**: Displays soil moisture logs via Chart.js and calculates irrigation runtimes in minutes.
6. **In-Browser AI Plant disease & Pest diagnostics**: Loads TensorFlow.js & MobileNet v2 models directly in the browser. Classifies potato blights, armyworms, grasshoppers, and aphids.
7. **Expense Ledger Manager**: Interactive cash-flow sheets with income vs expenses category allocation graphs.
8. **Kannada/English Voice Assistant**: Speech recognition & text-to-speech engine matching Kannada and English voice navigation commands.
9. **Simulated Drone Monitoring**: Infrared NDVI multispectral crop health maps and radar tracking grid controls.
10. **Auto Report Generator**: One-click daily, weekly, monthly, and yearly summaries with dedicated `@media print` sheets for PDF printing.
11. **Admin feedback portal**: Dynamic sentiment analysis logs mapping emotions (Happy, Satisfied, Angry, Disappointed), keywords, and reply systems.

---

## 📂 Project Structure

```
smart-agri-app/
├── app.py                  # Main Flask application entrypoint & AI logic
├── database.sql            # SQLite database schema initialization & seed data
├── requirements.txt        # Python dependency packages
├── README.md               # Setup & deployment guides
├── uploads/                # User uploaded document files folder (Auto-created)
├── static/
│   ├── css/
│   │   └── style.css       # Custom styling, dark mode tokens, print overrides
│   └── js/
│       ├── main.js         # Voice Assistant, dark mode state, browser routing
│       ├── charts.js       # Chart.js dashboards configuration
│       └── ai.js           # TensorFlow.js & MobileNet image classifier
└── templates/
    ├── base.html           # Core layout scaffold with collapsible sidebar
    ├── login.html          # Authentication - Login form
    ├── register.html       # Authentication - Register form
    ├── profile.html        # Profile management & edit details
    ├── dashboard.html      # Central farmer dashboard
    ├── soil.html           # Soil inputs & health scores log
    ├── crop_rec.html       # Crop matches & cultivation recommendations
    ├── weather.html        # Multi-metric forecast panels
    ├── irrigation.html     # Moisture lines & water calculation volume
    ├── disease.html        # Leaf diagnostic camera scan & log history
    ├── pest.html           # Pest classification camera scan & log history
    ├── fertilizer.html     # Fertilizer dosage splits calculator
    ├── market.html         # Mandi APMC rates comparison sheets
    ├── finance.html        # Cash flow entries ledger
    ├── drone.html          # NDVI simulated maps & flight radar tracker
    ├── feedback.html       # Rating stars feedback suggestions box
    ├── feedback_admin.html # Admin panel sentiment gauges & reply form
    └── reports.html        # Report selector & print layout wrapper
```

---

## 🛠️ Local Installation & Execution Steps

### 1. Prerequisite Checks
Make sure you have **Python 3.8+** installed on your system.

### 2. Navigate to Project Folder
Open your terminal (PowerShell / Command Prompt on Windows) and navigate inside the workspace folder:
```bash
cd "c:\Users\THRIVENI H M\OneDrive\Documents\New folder"
```

### 3. Install Dependencies
Run the installation command to fetch Flask packages:
```bash
pip install -r requirements.txt
```

### 4. Boot the Web Application
Execute the Flask server:
```bash
python app.py
```

### 5. Access the Web UI
Open your browser and navigate to:
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 🔑 Default Accounts (For Testing)

To log in as a pre-configured administrator and test the feedback sentiment dashboard and replies, use:
- **Email**: `admin@smartagri.com`
- **Password**: `admin123`

To test as a standard farmer, simply click **Register Account** on the login page and sign up.

---

## 🛡️ Security Features Integrated

1. **User Security**:
   - High-grade password hashing utilizing Werkzeug's cryptographic PBKDF2 hashing functions.
   - Decorator-based session authentication guards (`@login_required`) blocking unauthorized entry.
   - Session keys generated securely.

2. **Data & Upload Security**:
   - Allowed extension check blocks unauthorized uploads (allows only `.png`, `.jpg`, `.jpeg`, and `.pdf`).
   - Secure filename sanitization (`secure_filename`) preventing directory traversal exploits.
   - Core server files have restricted upload storage paths.

3. **Database Security**:
   - All connection interfaces utilize parameterized statements (`?` bindings) to prevent SQL Injection exploits.
   - Database operations use secure thread handles.

---

## 🚀 Cloud Deployment Instructions

### A. Preparing and Deploying to GitHub
1. Create a `.gitignore` file inside the root folder to exclude temp files:
   ```txt
   *.pyc
   __pycache__/
   database.db
   uploads/*
   !uploads/.gitkeep
   instance/
   ```
2. Initialize Git, stage all project files, and commit:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Smart Agriculture application"
   ```
3. Create a repository on GitHub (e.g. `smart-agri-rural-tech`).
4. Link local git to GitHub and push:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
   git branch -M main
   git push -u origin main
   ```

### B. Deploying to Render.com (Free Flask Hosting)
1. Register/Login to [Render](https://render.com/).
2. Connect your GitHub account and select your `smart-agri-rural-tech` repository.
3. Configure the Web Service settings as follows:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (Note: Install `gunicorn` package or modify command to `python app.py`)
   *Tip: It is recommended to add `gunicorn` to your requirements.txt for Render deployment, or set the start command to `python app.py` since our code has `app.run(host='0.0.0.0', port=5000)` inside the main script.*
4. Click **Deploy Web Service**. Render will build and launch your application under a public URL (e.g., `https://smart-agri.onrender.com`).
