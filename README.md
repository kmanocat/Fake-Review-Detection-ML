# FakeReview AI - Professional Fake Review Detection System

A professional web application built with Flask and Machine Learning to detect deceptive/fake reviews from e-commerce product links or manual text input.

## Features
- **User Side:**
    - Secure Registration & Login.
    - Forgot/Reset Password functionality.
    - **Link Analysis:** Paste any product link to fetch data and analyze for authenticity.
    - **Manual Analysis:** Paste specific review text to test with AI.
    - **History:** Track all past analysis results.
    - **Dashboard:** Modern UI with real-time feedback.
- **Admin Side:**
    - Monitor all user activities and analysis results.
- **Tech Stack:**
    - **Backend:** Flask, Python, SQLite.
    - **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5 (Professional Glassmorphism Theme).
    - **AI/ML:** Decision Tree Classifier (trained on historical dataset).

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the Model:**
   Before running the app, train the AI model by running the script:
   ```bash
   python train_model.py
   ```
   *Note: This will download/create the dataset and save the model in the `models/` folder.*

3. **Run the Application:**
   ```bash
   python app.py
   ```

4. **Access the App:**
   - Open your browser and go to `http://127.0.0.1:5000`
   - **Admin Login:** Use `admin` / `admin123` at the Admin Login page.

## Project Structure
- `app.py`: Main Flask application.
- `train_model.py`: AI training script using Decision Tree algorithm.
- `database.db`: SQLite database (created automatically).
- `models/`: Contains the pickled model and vectorizer.
- `static/`: CSS, JS, and Images for the frontend.
- `templates/`: HTML templates for all pages.
- `dataset/`: Contains the training CSV file.

## Developer Note
The Link Analysis uses a simulated scraper for major domains like Amazon/Flipkart to ensure stability, as these sites often employ anti-bot measures. For other generic sites, it attempts to extract metadata directly.
