# Fake Review Detection System - Project Walkthrough

This project provides a complete solution for identifying fake reviews using Machine Learning (Decision Tree) and a professional Flask-based web interface.

## 1. Machine Learning Implementation (`train_model.py`)
- **Algorithm:** Decision Tree Classifier.
- **Dataset:** Uses a historical fake review dataset (Binary classification: Genuine vs Fake).
- **Process:** 
  - Text preprocessing using **TF-IDF Vectorization**.
  - Training the Decision Tree model.
  - Exporting the trained model (`model.pkl`) and vectorizer for real-time predictions.

## 2. Backend Infrastructure (`app.py`)
- **Framework:** Flask.
- **Database:** SQLite (manages Users, Admins, and Analysis History).
- **Security:** 
  - Session-based authentication for Users and Admins.
  - Password management (Register, Login, Forgot/Reset).
- **Key Routes:**
  - `/analyze_link`: Scrapes (simulated/real) product data and predicts authenticity.
  - `/analyze_text`: Direct AI prediction on user-provided text.
  - `/admin_dashboard`: Exclusive access for admins to view global activity logs.

## 3. Frontend Design (`static/`, `templates/`)
- **Theme:** Bright, modern theme with glassmorphism effects.
- **Components:**
  - **Landing Page:** Professional hero section with feature highlights.
  - **User Dashboard:** Multi-tab interface for Link vs Text analysis.
  - **Result Visuals:** Dynamic badges (Green for Genuine, Red for Fake) and product image previews.
  - **History Panel:** Chronological view of all past user detections.

## 4. How to Use
- **Register** as a new user.
- **Log in** to access your dashboard.
- **Paste a product link** (e.g., from Amazon) to see the AI analyze its reviews.
- **Toggle to Manual Analysis** to test specific sentences or paragraphs.

---
### Credentials
- **Admin User:** `admin`
- **Admin Password:** `admin123`
