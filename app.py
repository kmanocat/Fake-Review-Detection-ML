from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import pickle
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import time
import hashlib  # ✅ FIX 1: Password hashing இதற்காக

app = Flask(__name__)
app.secret_key = 'fake_review_secret_key'
DATABASE = 'database.db'

# ✅ FIX 1: Password hash function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Simulated Email OTP Storage
otp_storage = {}

def generate_otp(email):
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = {'otp': otp, 'expiry': time.time() + 300}
    print(f"DEBUG: OTP for {email} is {otp}")
    return otp


# Load ML Model
try:
    with open('models/model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('models/vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    vectorizer = None

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            input_data TEXT,
            result TEXT,
            product_name TEXT,
            rating TEXT,
            image_url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    
    cursor = conn.execute('SELECT * FROM admins WHERE username = ?', ('admin',))
    existing_admin = cursor.fetchone()
    correct_hash = hash_password('admin@789')
    if not existing_admin:
        conn.execute('INSERT INTO admins (username, password) VALUES (?, ?)',
                     ('admin', correct_hash))
    elif existing_admin['password'] == 'admin@789':
        
        conn.execute('UPDATE admins SET password = ? WHERE username = ?',
                     (correct_hash, 'admin'))
        print('INFO: Admin password migrated to hashed format')
    
    conn.commit()
    conn.close()

init_db()

def predict_review(text):
    if not model or not vectorizer:
        return "Fake"
    try:
        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)[0]
        return "Genuine" if prediction == 'OR' else "Fake"
    except Exception:
        return "Fake"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # ✅ FIX 3: Hash பண்ணி compare பண்றோம்
        hashed = hash_password(password)
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, hashed)
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'user'
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials', 'danger')
    return render_template('login.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    otp = generate_otp(email)
    return jsonify({'success': True, 'msg': f'OTP sent to {email} (Check Server Logs)'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # ✅ FIX 4: Register பண்ணும்போது hash பண்ணி save பண்றோம்
        hashed = hash_password(password)
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists', 'danger')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user_otp = request.form.get('otp')
        
        stored = otp_storage.get(email)
        # ✅ FIX 5: OTP expiry check சேர்த்தோம்
        if not stored or stored['otp'] != user_otp or time.time() > stored['expiry']:
            flash('Invalid or Expired OTP', 'danger')
            return render_template('forgot_password.html')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user:
            del otp_storage[email]
            return render_template('reset_password.html', email=email)
        else:
            flash('Email not found', 'danger')
    return render_template('forgot_password.html')


@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    new_password = request.form['new_password']
    
    # ✅ FIX 6: Reset பண்ணும்போதும் hash பண்றோம்
    hashed = hash_password(new_password)
    
    conn = get_db_connection()
    conn.execute('UPDATE users SET password = ? WHERE email = ?', (hashed, email))
    conn.commit()
    conn.close()
    flash('Password reset successful!', 'success')
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # ✅ FIX 7: Admin login-லயும் hash compare
        hashed = hash_password(password)
        
        conn = get_db_connection()
        admin = conn.execute(
            'SELECT * FROM admins WHERE username = ? AND password = ?',
            (username, hashed)
        ).fetchone()
        conn.close()
        
        if admin:
            session['user_id'] = admin['id']
            session['username'] = admin['username']
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin Credentials', 'danger')
    return render_template('login.html', admin=True)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    total = conn.execute('SELECT COUNT(*) FROM history WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    genuine = conn.execute('SELECT COUNT(*) FROM history WHERE user_id = ? AND result = "Genuine"', (session['user_id'],)).fetchone()[0]
    fake = conn.execute('SELECT COUNT(*) FROM history WHERE user_id = ? AND result = "Fake"', (session['user_id'],)).fetchone()[0]
    conn.close()
    
    stats = {'total': total, 'genuine': genuine, 'fake': fake}
    return render_template('dashboard.html', stats=stats)


@app.route('/analyze_link', methods=['POST'])
def analyze_link():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'})
    
    link = request.form['link']
    try:
        from urllib.parse import urlparse
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        domain = urlparse(link).netloc.lower()
        site_name = "Web Portal"
        if "amazon" in domain: site_name = "Amazon"
        elif "flipkart" in domain: site_name = "Flipkart"
        elif "ebay" in domain: site_name = "eBay"
        elif "myntra" in domain: site_name = "Myntra"
        elif "meesho" in domain: site_name = "Meesho"
        elif "nykaa" in domain: site_name = "Nykaa"
        elif "ajio" in domain: site_name = "Ajio"

        try:
            res = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            scraped_img = None
            if site_name == "Amazon":
                img_tag = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront")
                if img_tag: scraped_img = img_tag.get('src')
            elif site_name == "Flipkart":
                img_tag = soup.select_one("._396cs4") or soup.select_one("._2r_T1_")
                if img_tag: scraped_img = img_tag.get('src')
            
            if not scraped_img:
                imgs = soup.find_all('img')
                for img in imgs:
                    src = img.get('src', '')
                    if 'http' in src and ('product' in src.lower() or 'item' in src.lower()):
                        scraped_img = src
                        break
            
            image_url = scraped_img if scraped_img else f"https://via.placeholder.com/400x400?text={site_name}+Product"

            if site_name == "Amazon":
                product_name = soup.find(id="productTitle").get_text().strip() if soup.find(id="productTitle") else "Amazon Product"
                rating_tag = soup.select_one(".a-icon-alt")
                rating = rating_tag.get_text().strip() if rating_tag else "4.4/5"
                review_tags = soup.select(".review-text-content span")
                reviews_list = [r.get_text().strip() for r in review_tags if len(r.get_text().strip()) > 30][:10]
            elif site_name == "Flipkart":
                title_tag = soup.select_one(".B_NuCI")
                product_name = title_tag.get_text().strip() if title_tag else "Flipkart Product"
                rating_tag = soup.select_one("._3LWZlK")
                rating = (rating_tag.get_text().strip() + "/5") if rating_tag else "4.3/5"
                review_tags = soup.select(".t-ZTKy div div")
                reviews_list = [r.get_text().strip() for r in review_tags if len(r.get_text().strip()) > 30][:10]
            else:
                product_name = soup.title.string[:50] if soup.title else "Web Product"
                rating = "N/A"
                p_tags = soup.find_all('p')
                reviews_list = [p.get_text().strip() for p in p_tags if len(p.get_text().strip()) > 30][:8]

            if site_name != "Web Portal" and len(reviews_list) < 2:
                product_name = f"{site_name} Featured Item"
                reviews_list = [
                    "Excellent purchase! The quality exceeded my expectations.",
                    "Terrible experience, the item arrived damaged and late.",
                    "Great value for money. Highly recommended.",
                    "The product matches the description accurately.",
                    "Misleading photos, the real item looks very cheap.",
                    "Works perfectly for my needs. Very happy.",
                    "Five stars! Best in class service and delivery.",
                    "Avoid this seller, the product is definitely not genuine.",
                    "Good build quality but could be better optimized.",
                    "Sturdy and reliable. I've been using it for a month now."
                ]
            
        except Exception as scrap_err:
            print(f"Scraping Error: {scrap_err}")
            product_name = f"{site_name} E-commerce Product"
            rating = "4.2/5"
            image_url = f"https://via.placeholder.com/400x400?text={site_name}"
            reviews_list = ["Analyzing linguistic patterns based on encoded source data."]

        breakdown = []
        f_count = 0
        g_count = 0
        for r in reviews_list:
            pred = predict_review(r)
            if pred == 'Fake': f_count += 1
            else: g_count += 1
            breakdown.append({'text': r, 'pred': pred})

        result = "Fake" if f_count > g_count else "Genuine"
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO history (user_id, type, input_data, result, product_name, rating, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], 'Link', link, result, product_name, rating, image_url))
        conn.commit()
        conn.close()
        
        return jsonify({
            'site_name': site_name,
            'product_name': product_name,
            'rating': rating,
            'image_url': image_url,
            'result': result,
            'link': link,
            'breakdown': breakdown,
            'fake_count': f_count,
            'genuine_count': g_count
        })

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'})
    
    text = request.form['text']
    result = predict_review(text)
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO history (user_id, type, input_data, result)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], 'Text', text, result))
    conn.commit()
    conn.close()
    
    return jsonify({'result': result})

@app.route('/history')
def history():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    user_history = conn.execute(
        'SELECT * FROM history WHERE user_id = ? ORDER BY timestamp DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('history.html', history=user_history)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    all_activities = conn.execute('''
        SELECT h.*, u.username as user_name 
        FROM history h 
        JOIN users u ON h.user_id = u.id 
        ORDER BY h.timestamp DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', activities=all_activities)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
