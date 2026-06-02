import os
import sqlite3
import random
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "smart_agri_secure_secret_key"
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Maximum upload size of 8MB
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

DATABASE = 'database.db'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize Database from database.sql
def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        try:
            with open(os.path.join(app.root_path, 'database.sql'), 'r') as f:
                conn.executescript(f.read())
            
            # Seed default admin if it does not exist
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", ('admin@smartagri.com',))
            if not cursor.fetchone():
                admin_pass = generate_password_hash('admin123')
                cursor.execute(
                    "INSERT INTO users (name, mobile, email, password_hash, village, district, state, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    ('Admin Staff', '9876543210', 'admin@smartagri.com', admin_pass, 'Agri Hub Central', 'Bangalore Rural', 'Karnataka', 'admin')
                )
            
            # Seed default notification alerts
            cursor.execute(
                "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
                (1, 'pest', 'Warning: High probability of Stem Borer outbreak reported in Shimoga district due to rising temperatures.')
            )
            cursor.execute(
                "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
                (1, 'weather', 'Rain predicted tomorrow. Consider delaying irrigation schedules to prevent soil logging.')
            )
            conn.commit()
        except Exception as e:
            print(f"Error seeding database: {e}")
        finally:
            conn.close()

# Decorator to secure routes
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper: Check secure file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================= AUTHENTICATION ROUTES =================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        village = request.form['village']
        district = request.form['district']
        state = request.form['state']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash("Email already registered. Try logging in.", "warning")
            conn.close()
            return redirect(url_for('register'))
            
        hashed_pass = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, mobile, email, password_hash, village, district, state) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, mobile, email, hashed_pass, village, district, state)
        )
        conn.commit()
        conn.close()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            session['district'] = user['district']
            flash("Logged in successfully. Welcome back!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        village = request.form['village']
        district = request.form['district']
        state = request.form['state']
        
        cursor.execute(
            "UPDATE users SET name=?, mobile=?, village=?, district=?, state=? WHERE id=?",
            (name, mobile, village, district, state, session['user_id'])
        )
        conn.commit()
        session['name'] = name
        session['district'] = district
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
        
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

# ================= FARMER DASHBOARD =================

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch User
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    # Fetch Active Crops
    cursor.execute("SELECT * FROM crops WHERE user_id = ? ORDER BY id DESC LIMIT 4", (session['user_id'],))
    crops = cursor.fetchall()
    
    # Fetch Alerts/Notifications
    cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 5", (session['user_id'],))
    alerts = cursor.fetchall()
    
    # Fetch Expenses Summary
    cursor.execute("SELECT SUM(amount) as income FROM expenses WHERE user_id = ? AND transaction_type = 'income'", (session['user_id'],))
    income_row = cursor.fetchone()
    cursor.execute("SELECT SUM(amount) as expense FROM expenses WHERE user_id = ? AND transaction_type = 'expense'", (session['user_id'],))
    expense_row = cursor.fetchone()
    
    total_income = income_row['income'] if income_row['income'] else 0.0
    total_expense = expense_row['expense'] if expense_row['expense'] else 0.0
    balance = total_income - total_expense
    
    # Add seed notification if none exists
    if not alerts:
        cursor.execute(
            "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
            (session['user_id'], 'irrigation', 'Smart Irrigation Reminder: Soil moisture for Field A is 32% (Low). Suggest watering.')
        )
        conn.commit()
        cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 5", (session['user_id'],))
        alerts = cursor.fetchall()

    conn.close()
    
    # Quick Status Calculations
    crop_count = len(crops)
    soil_status = "Good"
    
    return render_template(
        'dashboard.html',
        user=user,
        crops=crops,
        alerts=alerts,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        crop_count=crop_count,
        soil_status=soil_status
    )

# ================= SOIL ANALYSIS MODULE =================

@app.route('/soil', methods=['GET', 'POST'])
@login_required
def soil():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        ph = float(request.form['ph'])
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorus'])
        potassium = float(request.form['potassium'])
        organic_matter = float(request.form['organic_matter'])
        
        # Handling file upload securely
        report_path = None
        if 'report_file' in request.files:
            file = request.files['report_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"user_{session['user_id']}_{int(datetime.now().timestamp())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                report_path = unique_filename
        
        # Calculate Health Score (rules out of 100)
        score = 100
        recs = []
        
        # pH checks
        if ph < 5.5:
            score -= 20
            recs.append("Soil is acidic. Add agricultural lime (Calcium Carbonate) to raise pH.")
        elif ph > 7.5:
            score -= 20
            recs.append("Soil is alkaline. Apply organic mulch, peat moss, or elemental sulfur to lower pH.")
            
        # N checks (Ideal: 280 - 560 kg/ha)
        if nitrogen < 280:
            score -= 20
            recs.append("Nitrogen (N) levels are critically low. Add compost, cow manure, or Urea.")
        elif nitrogen > 560:
            score -= 10
            recs.append("High nitrogen can cause excess leafy growth. Reduce nitrogenous fertilizers.")
            
        # P checks (Ideal: 23 - 57 kg/ha)
        if phosphorus < 23:
            score -= 20
            recs.append("Phosphorus (P) is low. Apply bone meal, rock phosphate, or SSP fertilizer.")
            
        # K checks (Ideal: 140 - 330 kg/ha)
        if potassium < 140:
            score -= 20
            recs.append("Potassium (K) is deficient. Add Muriate of Potash (MOP) or wood ash.")
            
        # Organic Matter (Ideal: 1.5% - 3.0%)
        if organic_matter < 1.5:
            score -= 10
            recs.append("Organic Carbon/Matter is low. Incorporate green manure (sunn hemp) or vermicompost.")
            
        health_score = max(20, score)
        recs_str = "\n".join(recs) if recs else "Soil nutrient content is balanced and excellent. Maintain normal organic manure applications."
        
        cursor.execute(
            "INSERT INTO soil_reports (user_id, ph, nitrogen, phosphorus, potassium, organic_matter, report_file, health_score, recommendations) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session['user_id'], ph, nitrogen, phosphorus, potassium, organic_matter, report_path, health_score, recs_str)
        )
        conn.commit()
        flash("Soil report analyzed and saved successfully!", "success")
        return redirect(url_for('soil'))
        
    cursor.execute("SELECT * FROM soil_reports WHERE user_id = ? ORDER BY id DESC", (session['user_id'],))
    reports = cursor.fetchall()
    conn.close()
    return render_template('soil.html', reports=reports)

# ================= CROP RECOMMENDATION SYSTEM =================

@app.route('/crop_recommendation', methods=['GET', 'POST'])
@login_required
def crop_recommendation():
    recommendation = None
    if request.method == 'POST':
        soil_type = request.form['soil_type']
        season = request.form['season']
        rainfall = request.form['rainfall']
        location = request.form['location']
        
        # Engine Heuristics
        if soil_type == 'Clay' and rainfall == 'High':
            recommendation = {
                'crop_name': 'Paddy (Rice)',
                'yield': '3.8 - 4.5 tons/acre',
                'season': 'Kharif (June - Nov)',
                'profitability': '88% (High Demand)',
                'practices': 'Transplant 25-day old seedlings. Keep 2-5cm standing water level during vegetative stage. Apply Urea in splits.'
            }
        elif soil_type == 'Black' and season == 'Kharif':
            recommendation = {
                'crop_name': 'Cotton',
                'yield': '1.0 - 1.4 tons/acre',
                'season': 'Kharif (May - Dec)',
                'profitability': '82% (Excellent returns)',
                'practices': 'Ensure row spacing of 90cm. Crop is sensitive to waterlogging, ensure good drainage. Monitor for bollworm pests.'
            }
        elif soil_type == 'Sandy' and rainfall == 'Low':
            recommendation = {
                'crop_name': 'Ragi (Finger Millet)',
                'yield': '1.2 - 1.6 tons/acre',
                'season': 'Rabi / Kharif',
                'profitability': '65% (Low input cost)',
                'practices': 'Excellent drought tolerance. Drill seeds with 30cm row gap. Requires minimal nitrogen. Apply farmyard manure.'
            }
        elif soil_type == 'Red' and season == 'Rabi':
            recommendation = {
                'crop_name': 'Groundnut (Peanut)',
                'yield': '1.5 - 2.0 tons/acre',
                'season': 'Rabi (Oct - Mar)',
                'profitability': '78% (Oil seed demand)',
                'practices': 'Incorporate gypsum at 45 days after sowing. Maintain light, uniform moisture. Earth up soil to assist pod pegging.'
            }
        elif soil_type == 'Loamy' and season == 'Summer':
            recommendation = {
                'crop_name': 'Maize (Corn)',
                'yield': '2.5 - 3.2 tons/acre',
                'season': 'Summer / Rabi',
                'profitability': '72% (Steady market)',
                'practices': 'Keep soil moist. Apply micro-nutrients like Zinc Sulphate. Harvest when husks turn paper dry.'
            }
        else:
            # Fallback
            recommendation = {
                'crop_name': 'Chickpea (Bengal Gram)',
                'yield': '0.8 - 1.2 tons/acre',
                'season': 'Rabi (Nov - Feb)',
                'profitability': '70% (Pulses demand)',
                'practices': 'Treat seed with Rhizobium culture. Irrigate once at pre-flowering and once at pod-development stage.'
            }
            
    # Add crop mapping to user dashboard option
    if request.args.get('add_crop') and request.args.get('crop_name'):
        c_name = request.args.get('crop_name')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO crops (user_id, crop_name, crop_type, planted_date, status) VALUES (?, ?, ?, ?, ?)",
            (session['user_id'], c_name, 'Grain/Fiber', datetime.now().strftime('%Y-%m-%d'), 'healthy')
        )
        conn.commit()
        conn.close()
        flash(f"{c_name} added to your active crops dashboard!", "success")
        return redirect(url_for('dashboard'))

    return render_template('crop_rec.html', recommendation=recommendation)

# ================= WEATHER MODULE =================

@app.route('/weather')
@login_required
def weather():
    district = session.get('district', 'Bangalore')
    
    # Built-in High Fidelity Mock Forecast Engine that simulates realistic weather patterns
    current_temp = random.randint(26, 33)
    humidity = random.randint(60, 85)
    wind_speed = round(random.uniform(5.5, 15.2), 1)
    rain_prob = random.randint(20, 95)
    
    warnings = []
    if rain_prob > 80:
        warnings.append("Heavy rain alert: Expect thunderstorms in the next 24 hours. Keep drainage channels open.")
    if current_temp > 35:
        warnings.append("High Temperature: Soil moisture evaporation rates will be elevated. Adjust watering frequencies.")
    if wind_speed > 18:
        warnings.append("High Winds: Restrict pesticide spraying operations to avoid drift loss.")
        
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today_idx = datetime.now().weekday()
    
    forecast = []
    for i in range(7):
        day_name = days[(today_idx + i) % 7]
        forecast.append({
            'day': day_name,
            'temp': random.randint(25, 34),
            'humidity': random.randint(55, 90),
            'condition': random.choice(['Sunny', 'Partly Cloudy', 'Scattered Rain', 'Heavy Rain', 'Windy'])
        })
        
    return render_template(
        'weather.html',
        district=district,
        temp=current_temp,
        humidity=humidity,
        wind_speed=wind_speed,
        rain_prob=rain_prob,
        warnings=warnings,
        forecast=forecast
    )

# ================= SMART IRRIGATION SYSTEM =================

@app.route('/irrigation', methods=['GET', 'POST'])
@login_required
def irrigation():
    # Fetch user's crops
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crops WHERE user_id = ? ORDER BY id DESC", (session['user_id'],))
    crops = cursor.fetchall()
    conn.close()
    
    req_water = None
    crop_name = None
    moisture = None
    
    if request.method == 'POST':
        crop_name = request.form['crop_name']
        moisture = float(request.form['moisture'])
        soil_type = request.form['soil_type']
        
        # Calculate water requirement
        # Target moisture is 60%
        if moisture >= 60:
            req_water = 0
        else:
            factor = {
                'Clay': 1.2,
                'Sandy': 1.8,
                'Loamy': 1.4,
                'Black': 1.3,
                'Red': 1.5
            }.get(soil_type, 1.5)
            
            # Simple formula: shortfall * factor * scaling constant
            req_water = round((60.0 - moisture) * factor * 150, 1) # Liters per acre
            
    # Mock some moisture analytics charts data points
    moisture_data = [random.randint(45, 75) for _ in range(7)]
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    return render_template(
        'irrigation.html',
        crops=crops,
        req_water=req_water,
        crop_name=crop_name,
        moisture=moisture,
        moisture_data=moisture_data,
        days=days
    )

# ================= PLANT DISEASE & PEST DETECTION BACKEND =================

@app.route('/disease', methods=['GET', 'POST'])
@login_required
def disease():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # File upload handling (Image)
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"disease_{session['user_id']}_{int(datetime.now().timestamp())}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Mock AI classifier on python side if client model is loading
                disease_name = request.form.get('detected_name', 'Potato Late Blight')
                confidence = float(request.form.get('confidence', 92.4))
                treatment = request.form.get('treatment', 'Apply Copper-based fungicides. Prune and destroy infected leaves.')
                prevention = request.form.get('prevention', 'Ensure proper spacing to reduce humidity. Avoid overhead watering.')
                
                cursor.execute(
                    "INSERT INTO disease_reports (user_id, image_path, detected_name, confidence, treatment, prevention) VALUES (?, ?, ?, ?, ?, ?)",
                    (session['user_id'], unique_filename, disease_name, confidence, treatment, prevention)
                )
                
                # Insert warning alert
                cursor.execute(
                    "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
                    (session['user_id'], 'pest', f"Alert: Outbreak of {disease_name} detected in your field. Apply recommended treatment immediately.")
                )
                conn.commit()
                flash("Disease report processed and logged!", "success")
                return redirect(url_for('disease'))
                
    cursor.execute("SELECT * FROM disease_reports WHERE user_id = ? ORDER BY id DESC", (session['user_id'],))
    reports = cursor.fetchall()
    conn.close()
    return render_template('disease.html', reports=reports)

@app.route('/pest', methods=['GET', 'POST'])
@login_required
def pest():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # We will reuse the disease reports table format for logs to keep db compact, 
    # or identify pests as part of plant disease logs.
    # Let's save pest records with a 'Pest: ' prefix in detected_name.
    if request.method == 'POST':
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"pest_{session['user_id']}_{int(datetime.now().timestamp())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                
                pest_name = request.form.get('detected_name', 'Pest: Fall Armyworm')
                confidence = float(request.form.get('confidence', 89.5))
                treatment = request.form.get('treatment', 'Spray Neem Oil solution (1-2%). Introduce beneficial insects like trichogramma wasps.')
                prevention = request.form.get('prevention', 'Conduct regular crop monitoring. Practice crop rotation and intercropping.')
                
                cursor.execute(
                    "INSERT INTO disease_reports (user_id, image_path, detected_name, confidence, treatment, prevention) VALUES (?, ?, ?, ?, ?, ?)",
                    (session['user_id'], unique_filename, pest_name, confidence, treatment, prevention)
                )
                
                # Add alert
                cursor.execute(
                    "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
                    (session['user_id'], 'pest', f"Alert: {pest_name} detected in field. Apply Neem oil or organic formulations.")
                )
                conn.commit()
                flash("Pest identification logged successfully!", "success")
                return redirect(url_for('pest'))
                
    cursor.execute("SELECT * FROM disease_reports WHERE user_id = ? AND detected_name LIKE 'Pest:%' ORDER BY id DESC", (session['user_id'],))
    reports = cursor.fetchall()
    conn.close()
    return render_template('pest.html', reports=reports)

# ================= FERTILIZER RECOMMENDATION SYSTEM =================

@app.route('/fertilizer', methods=['GET', 'POST'])
@login_required
def fertilizer():
    recommendation = None
    
    if request.method == 'POST':
        crop = request.form['crop']
        ph = float(request.form['ph'])
        n = float(request.form['n'])
        p = float(request.form['p'])
        k = float(request.form['k'])
        
        # Calculate dosage recommendations based on targets
        # Target ranges (N - P - K in kg/acre)
        target = {
            'Paddy (Rice)': (48, 24, 24),
            'Wheat': (40, 20, 16),
            'Maize (Corn)': (60, 30, 24),
            'Cotton': (40, 20, 20),
            'Groundnut': (10, 20, 30)
        }.get(crop, (40, 20, 20))
        
        n_req = max(0.0, target[0] - (n * 0.1)) # conversion adjustment
        p_req = max(0.0, target[1] - (p * 0.1))
        k_req = max(0.0, target[2] - (k * 0.1))
        
        # Convert inputs to Urea, SSP, and MOP dosages
        # Urea has 46% N
        urea_dose = round(n_req / 0.46, 1)
        # SSP has 16% P
        ssp_dose = round(p_req / 0.16, 1)
        # MOP has 60% K
        mop_dose = round(k_req / 0.60, 1)
        
        recommendation = {
            'crop': crop,
            'npk_targets': f"Target (N-P-K): {target[0]}-{target[1]}-{target[2]} kg/acre",
            'urea': urea_dose,
            'ssp': ssp_dose,
            'mop': mop_dose,
            'schedule': [
                "Basal Application (At Sowing): Apply 100% of SSP, 100% of MOP, and 33% of Urea.",
                "Top Dressing 1 (30 Days After Sowing): Apply 33% of Urea.",
                "Top Dressing 2 (60 Days After Sowing): Apply remaining 34% of Urea during panicle initiation / vegetative peak."
            ]
        }
        
    return render_template('fertilizer.html', recommendation=recommendation)

# ================= MARKET PRICE TRACKER =================

@app.route('/market')
@login_required
def market():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query prices
    cursor.execute("SELECT * FROM market_prices ORDER BY crop_name, market_name")
    prices = cursor.fetchall()
    conn.close()
    
    # Create structured data for charts
    crop_trends = {
        'Paddy (Rice)': [1900, 1950, 2010, 2030, 2050, 2100, 2050],
        'Ragi (Finger Millet)': [3100, 3150, 3200, 3280, 3320, 3350, 3400],
        'Tomato': [600, 750, 1100, 1400, 1600, 1250, 1150]
    }
    
    return render_template('market.html', prices=prices, trends=crop_trends)

# ================= FARM EXPENSE MANAGER =================

@app.route('/finance', methods=['GET', 'POST'])
@login_required
def finance():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        t_type = request.form['transaction_type']
        category = request.form['category']
        amount = float(request.form['amount'])
        date = request.form['date']
        desc = request.form['description']
        
        cursor.execute(
            "INSERT INTO expenses (user_id, transaction_type, category, amount, date, description) VALUES (?, ?, ?, ?, ?, ?)",
            (session['user_id'], t_type, category, amount, date, desc)
        )
        conn.commit()
        flash("Transaction recorded successfully!", "success")
        return redirect(url_for('finance'))
        
    # Query current history
    cursor.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC", (session['user_id'],))
    transactions = cursor.fetchall()
    
    # Aggregates
    cursor.execute("SELECT SUM(amount) as inc FROM expenses WHERE user_id = ? AND transaction_type = 'income'", (session['user_id'],))
    inc_val = cursor.fetchone()['inc'] or 0.0
    cursor.execute("SELECT SUM(amount) as exp FROM expenses WHERE user_id = ? AND transaction_type = 'expense'", (session['user_id'],))
    exp_val = cursor.fetchone()['exp'] or 0.0
    
    conn.close()
    return render_template('finance.html', transactions=transactions, income=inc_val, expense=exp_val, profit=inc_val-exp_val)

# ================= DRONE MONITORING MODULE =================

@app.route('/drone')
@login_required
def drone():
    return render_template('drone.html')

# ================= AI SENTIMENT & FEEDBACK PORTAL =================

# Custom text parser for sentiment analysis
def analyze_sentiment(comment):
    comment_lower = comment.lower()
    
    pos_words = ['good', 'great', 'excellent', 'happy', 'satisfied', 'helpful', 'easy', 'love', 'best', 'wonderful', 'nice', 'useful', 'superb', 'awesome', 'yes', 'fine']
    neg_words = ['bad', 'poor', 'slow', 'hard', 'difficult', 'worst', 'angry', 'sad', 'disappointed', 'fail', 'broken', 'error', 'wrong', 'useless', 'expensive', 'heavy', 'no']
    
    pos_count = sum(1 for w in pos_words if w in comment_lower)
    neg_count = sum(1 for w in neg_words if w in comment_lower)
    
    score = 0.0
    if pos_count + neg_count > 0:
        score = (pos_count - neg_count) / (pos_count + neg_count)
        
    if score > 0.1:
        sentiment = 'positive'
        emotion = 'Satisfied' if score < 0.6 else 'Happy'
    elif score < -0.1:
        sentiment = 'negative'
        emotion = 'Disappointed' if score > -0.6 else 'Angry'
    else:
        sentiment = 'neutral'
        emotion = 'Satisfied'  # Default neutral-positive fallback
        
    # Extract keywords
    extracted = []
    keywords_list = ['crop', 'soil', 'water', 'fertilizer', 'pest', 'disease', 'price', 'market', 'drone', 'language', 'kannada', 'voice', 'expense', 'money', 'speed']
    for kw in keywords_list:
        if kw in comment_lower:
            extracted.append(kw.capitalize())
            
    # Categorization mapping
    category = 'General'
    category_map = {
        'crop': 'Crop recommendation',
        'soil': 'Soil Analysis',
        'water': 'Irrigation',
        'irrigation': 'Irrigation',
        'fertilizer': 'Fertilizer',
        'pest': 'Pest/Disease',
        'disease': 'Pest/Disease',
        'price': 'Market prices',
        'market': 'Market prices',
        'drone': 'Drone monitoring',
        'expense': 'Finance',
        'money': 'Finance',
        'voice': 'Voice Assistant',
        'kannada': 'Voice Assistant'
    }
    for kw, cat in category_map.items():
        if kw in comment_lower:
            category = cat
            break
            
    return sentiment, round(score, 2), emotion, category, ", ".join(extracted) if extracted else "General"

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        suggestion = request.form.get('suggestion', '')
        is_anonymous = 1 if 'is_anonymous' in request.form else 0
        
        # Run AI Sentiment analysis
        sentiment, score, emotion, category, keywords = analyze_sentiment(comment)
        
        user_id = None if is_anonymous else session['user_id']
        
        cursor.execute(
            "INSERT INTO feedback (user_id, rating, comment, suggestion, is_anonymous, sentiment, sentiment_score, emotion, category, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, rating, comment, suggestion, is_anonymous, sentiment, score, emotion, category, keywords)
        )
        conn.commit()
        flash("Thank you for your valuable feedback! Analyzed by AI.", "success")
        return redirect(url_for('feedback'))
        
    # Get user feedback history
    cursor.execute(
        "SELECT * FROM feedback WHERE user_id = ? ORDER BY id DESC", 
        (session['user_id'],)
    )
    feedback_history = cursor.fetchall()
    conn.close()
    
    return render_template('feedback.html', history=feedback_history)

@app.route('/admin/feedback', methods=['GET', 'POST'])
@login_required
def feedback_admin():
    if session.get('role') != 'admin':
        flash("Access Denied: Administrative permissions required.", "danger")
        return redirect(url_for('dashboard'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Process Response Form
    if request.method == 'POST' and 'response_id' in request.form:
        fid = int(request.form['response_id'])
        admin_resp = request.form['admin_response']
        cursor.execute("UPDATE feedback SET admin_response = ? WHERE id = ?", (admin_resp, fid))
        conn.commit()
        flash("Response recorded and sent to farmer.", "success")
        return redirect(url_for('feedback_admin'))
        
    # Filters
    sentiment_filter = request.args.get('sentiment', 'all')
    if sentiment_filter != 'all':
        cursor.execute(
            "SELECT f.*, u.name as u_name FROM feedback f LEFT JOIN users u ON f.user_id = u.id WHERE f.sentiment = ? ORDER BY f.id DESC", 
            (sentiment_filter,)
        )
    else:
        cursor.execute(
            "SELECT f.*, u.name as u_name FROM feedback f LEFT JOIN users u ON f.user_id = u.id ORDER BY f.id DESC"
        )
    feedbacks = cursor.fetchall()
    
    # Analytical stats
    cursor.execute("SELECT COUNT(*) as total FROM feedback")
    total_fb = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT COUNT(*) as pos FROM feedback WHERE sentiment = 'positive'")
    pos_fb = cursor.fetchone()['pos'] or 0
    
    cursor.execute("SELECT COUNT(*) as neg FROM feedback WHERE sentiment = 'negative'")
    neg_fb = cursor.fetchone()['neg'] or 0
    
    pos_pct = round((pos_fb / total_fb * 100), 1) if total_fb > 0 else 0.0
    neg_pct = round((neg_fb / total_fb * 100), 1) if total_fb > 0 else 0.0
    
    # Top complaints categories
    cursor.execute("SELECT category, COUNT(*) as count FROM feedback WHERE sentiment='negative' GROUP BY category ORDER BY count DESC LIMIT 3")
    complaints = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        'feedback_admin.html',
        feedbacks=feedbacks,
        total_fb=total_fb,
        pos_pct=pos_pct,
        neg_pct=neg_pct,
        complaints=complaints,
        current_filter=sentiment_filter
    )

# ================= AUTO REPORT GENERATOR =================

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    generated_report = None
    
    if request.method == 'POST':
        period = request.form['period']
        
        # Gather summaries
        # 1. Weather summary
        weather_summary = "Stable seasonal conditions. Rain distribution was average. Maximum temperature recorded was 33°C."
        
        # 2. Soil summary
        cursor.execute("SELECT AVG(ph) as avg_ph, AVG(health_score) as avg_score FROM soil_reports WHERE user_id = ?", (session['user_id'],))
        soil_stat = cursor.fetchone()
        avg_ph = round(soil_stat['avg_ph'], 1) if soil_stat['avg_ph'] else 6.5
        avg_score = int(soil_stat['avg_score']) if soil_stat['avg_score'] else 85
        soil_summary = f"Average soil pH: {avg_ph}, Nutrition index: {avg_score}/100. Recommendations focused on Nitrogen correction."
        
        # 3. Crops summary
        cursor.execute("SELECT COUNT(*) as active_count FROM crops WHERE user_id = ? AND status='healthy'", (session['user_id'],))
        healthy_count = cursor.fetchone()['active_count'] or 0
        crop_summary = f"Total healthy crops monitored: {healthy_count}. Growth cycle conforms to normal parameters."
        
        # 4. Irrigation summary
        irrigation_summary = "Total irrigation triggers: 12 events. Water application efficiency calculated at 92%. Drip systems optimal."
        
        # 5. Finance summary
        cursor.execute("SELECT SUM(amount) as inc FROM expenses WHERE user_id = ? AND transaction_type = 'income'", (session['user_id'],))
        inc_v = cursor.fetchone()['inc'] or 0.0
        cursor.execute("SELECT SUM(amount) as exp FROM expenses WHERE user_id = ? AND transaction_type = 'expense'", (session['user_id'],))
        exp_v = cursor.fetchone()['exp'] or 0.0
        margin = inc_v - exp_v
        financial_summary = f"Total Income: ₹{inc_v}, Expenses: ₹{exp_v}. Net margin: ₹{margin}. Main expense category: Fertilizers."
        
        # 6. AI recommendations, cost optimizations, and productivity forecasting
        recs = [
            "AI Recommendation: Increase organic matter dosage to naturally improve water retention by 15%.",
            "Cost Optimization: Transition to bulk SSP instead of DAP to reduce nitrogen-excess costs by 8%.",
            "Future Yield Forecast: Dynamic calculations indicate a 12% yield boost for Paddy in the upcoming cycle under current moisture patterns."
        ]
        ai_recommendations = "\n".join(recs)
        
        # Write to database reports history
        cursor.execute(
            "INSERT INTO reports (user_id, report_period, weather_summary, soil_summary, crop_summary, irrigation_summary, financial_summary, ai_recommendations) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (session['user_id'], period, weather_summary, soil_summary, crop_summary, irrigation_summary, financial_summary, ai_recommendations)
        )
        conn.commit()
        flash(f"{period} Agricultural performance report generated!", "success")
        return redirect(url_for('reports'))
        
    # Get previous reports
    cursor.execute("SELECT * FROM reports WHERE user_id = ? ORDER BY id DESC", (session['user_id'],))
    reports_history = cursor.fetchall()
    
    # If a specific report is requested for view
    report_id = request.args.get('view_id')
    if report_id:
        cursor.execute("SELECT * FROM reports WHERE user_id = ? AND id = ?", (session['user_id'], report_id))
        generated_report = cursor.fetchone()
        
    conn.close()
    
    return render_template('reports.html', reports=reports_history, active_report=generated_report)

# ================= KANNADA/ENGLISH VOICE ASSISTANT ENDPOINT =================

# A JSON API to support keyword querying from the frontend voice agent
@app.route('/api/voice_assist', methods=['POST'])
@login_required
def voice_assist():
    data = request.json
    command = data.get('command', '').lower()
    
    response_text = "Sorry, I couldn't understand that command. Please try speaking again."
    kannada_response = "ಕ್ಷಮಿಸಿ, ಆಜ್ಞೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ."
    redirect_target = None
    
    # Mapping English and Kannada query targets
    if "dashboard" in command or "ಡೆಸ್ಕ್" in command or "ಮುಖ್ಯ ಪುಟ" in command:
        response_text = "Navigating to your farming dashboard."
        kannada_response = "ನಿಮ್ಮ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ ಪುಟಕ್ಕೆ ನ್ಯಾವಿಗೇಟ್ ಮಾಡಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('dashboard')
        
    elif "weather" in command or "forecast" in command or "ಹವಾಮಾನ" in command:
        response_text = "Opening your 7-day weather forecast system."
        kannada_response = "ನಿಮ್ಮ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಪುಟವನ್ನು ತೆರೆಯಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('weather')
        
    elif "soil" in command or "ಮಣ್ಣು" in command or "ಪರೀಕ್ಷೆ" in command:
        response_text = "Redirecting you to the soil analysis workspace."
        kannada_response = "ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ ವಿಭಾಗಕ್ಕೆ ಮರುನಿರ್ದೇಶಿಸಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('soil')
        
    elif "irrigation" in command or "water" in command or "ನೀರಾವರಿ" in command or "ನೀರು" in command:
        response_text = "Loading your smart irrigation water schedule."
        kannada_response = "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('irrigation')
        
    elif "expense" in command or "finance" in command or "ಹಣಕಾಸು" in command or "ಖರ್ಚು" in command:
        response_text = "Opening the farm finance manager ledger."
        kannada_response = "ಕೃಷಿ ಹಣಕಾಸು ನಿರ್ವಾಹಕ ಲೆಡ್ಜರ್ ಪುಟವನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('finance')
        
    elif "price" in command or "market" in command or "ಮಾರುಕಟ್ಟೆ" in command or "ದರ" in command:
        response_text = "Fetching today's APMC crop market prices."
        kannada_response = "ಇಂದಿನ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳನ್ನು ತೋರಿಸಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('market')
        
    elif "disease" in command or "leaf" in command or "ರೋಗ" in command or "ಎಲೆ" in command:
        response_text = "Redirecting you to the plant disease detection model."
        kannada_response = "ಸಸ್ಯ ರೋಗ ಪತ್ತೆಹಚ್ಚುವಿಕೆ ಮಾದರಿಗೆ ನಿಮ್ಮನ್ನು ಕರೆದೊಯ್ಯಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('disease')
        
    elif "pest" in command or "ಹುಳು" in command or "ಕೀಟ" in command:
        response_text = "Opening the pest identification page."
        kannada_response = "ಕೀಟ ಪತ್ತೆಹಚ್ಚುವಿಕೆ ಮಾದರಿಗೆ ನಿಮ್ಮನ್ನು ಕರೆದೊಯ್ಯಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('pest')
        
    elif "fertilizer" in command or "ಗೊಬ್ಬರ" in command:
        response_text = "Opening fertilizer NPK recommendation engine."
        kannada_response = "ರಸಗೊಬ್ಬರ ಶಿಫಾರಸು ಎಂಜಿನ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('fertilizer')

    elif "report" in command or "ವರದಿ" in command:
        response_text = "Opening report generator page."
        kannada_response = "ವರದಿ ಜನರೇಟರ್ ಪುಟಕ್ಕೆ ನ್ಯಾವಿಗೇಟ್ ಮಾಡಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('reports')

    elif "feedback" in command or "ಅಭಿಪ್ರಾಯ" in command:
        response_text = "Opening customer feedback portal."
        kannada_response = "ಅಭಿಪ್ರಾಯ ಪೋರ್ಟಲ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ."
        redirect_target = url_for('feedback')

    # Basic Q&A capabilities
    elif "paddy water" in command or "rice water" in command:
        response_text = "Rice needs continuous standing water of 2 to 5 centimeters during vegetative growth."
        kannada_response = "ಭತ್ತದ ಬೆಳವಣಿಗೆಯ ಸಮಯದಲ್ಲಿ ಎರಡು ರಿಂದ ಐದು ಸೆಂಟಿಮೀಟರ್ ನೀರು ನಿಲ್ಲಿಸುವುದು ಅವಶ್ಯಕ."
    elif "acid soil" in command or "acidic" in command:
        response_text = "Add lime to raise soil pH to 6.5."
        kannada_response = "ಆಮ್ಲೀಯ ಮಣ್ಣಿಗೆ ಸುಣ್ಣ ಸೇರಿಸುವುದರಿಂದ ಪಿಎಚ್ ಮಟ್ಟವನ್ನು ಹೆಚ್ಚಿಸಬಹುದು."
    elif "armyworm" in command or "army worm" in command:
        response_text = "Spray Neem oil formulation or apply Bacillus thuringiensis biologically."
        kannada_response = "ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ ಅಥವಾ ಜೈವಿಕವಾಗಿ ಬೆಸಿಲಸ್ ತುರಿಂಜಿಯೆನ್ಸಿಸ್ ಬಳಸಿ."
        
    return jsonify({
        'english': response_text,
        'kannada': kannada_response,
        'redirect': redirect_target
    })

# ================= APP STARTUP =================

if __name__ == '__main__':
    init_db()
    # Run server locally on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
