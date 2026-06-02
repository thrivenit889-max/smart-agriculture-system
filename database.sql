-- Database Schema for Smart Agriculture and Rural Tech Web Application

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    village TEXT NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'farmer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crops Table
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    crop_name TEXT NOT NULL,
    crop_type TEXT NOT NULL,
    planted_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'healthy',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Expenses Table
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Soil Reports Table
CREATE TABLE IF NOT EXISTS soil_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ph REAL NOT NULL,
    nitrogen REAL NOT NULL,
    phosphorus REAL NOT NULL,
    potassium REAL NOT NULL,
    organic_matter REAL NOT NULL,
    report_file TEXT,
    health_score INTEGER NOT NULL,
    recommendations TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Disease Reports Table
CREATE TABLE IF NOT EXISTS disease_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    detected_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    treatment TEXT NOT NULL,
    prevention TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Market Prices Table
CREATE TABLE IF NOT EXISTS market_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name TEXT NOT NULL,
    market_name TEXT NOT NULL,
    min_price REAL NOT NULL,
    max_price REAL NOT NULL,
    avg_price REAL NOT NULL,
    price_date TEXT NOT NULL
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL,
    suggestion TEXT,
    is_anonymous INTEGER NOT NULL DEFAULT 0,
    sentiment TEXT NOT NULL,
    sentiment_score REAL NOT NULL,
    emotion TEXT NOT NULL,
    category TEXT NOT NULL,
    keywords TEXT,
    admin_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    report_period TEXT NOT NULL,
    weather_summary TEXT,
    soil_summary TEXT,
    crop_summary TEXT,
    irrigation_summary TEXT,
    financial_summary TEXT,
    ai_recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert Seed Market Prices
INSERT INTO market_prices (crop_name, market_name, min_price, max_price, avg_price, price_date) VALUES
('Paddy (Rice)', 'Shimoga APMC', 1800, 2200, 2050, CURRENT_DATE),
('Paddy (Rice)', 'Davangere APMC', 1850, 2250, 2100, CURRENT_DATE),
('Ragi (Finger Millet)', 'Bangalore APMC', 3100, 3600, 3400, CURRENT_DATE),
('Ragi (Finger Millet)', 'Mysore APMC', 3050, 3500, 3300, CURRENT_DATE),
('Maize (Corn)', 'Challakere APMC', 1600, 1950, 1820, CURRENT_DATE),
('Jowar (Sorghum)', 'Hubli APMC', 2400, 2900, 2700, CURRENT_DATE),
('Cotton', 'Raichur APMC', 6000, 7500, 6900, CURRENT_DATE),
('Onion', 'Chikballapur APMC', 1200, 1800, 1500, CURRENT_DATE),
('Tomato', 'Kolar APMC', 800, 1500, 1150, CURRENT_DATE);
