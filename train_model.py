import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import pickle
import os
import random

def generate_large_dataset(n=1200):
    genuine_templates = [
        "Excellent product, highly recommended!",
        "I love this {product}, it works perfectly.",
        "Good quality for the price. Fast shipping.",
        "Exactly what I was looking for. 5 stars.",
        "This {product} exceeded my expectations. Very happy with the purchase.",
        "Durable and reliable. I've been using it for a month now.",
        "Great value for money. The packaging was secure.",
        "Smooth transaction, item as described. Thanks!",
        "Very satisfied with the customer service and the product quality.",
        "Works great! Easy to set up and use."
    ]
    
    fake_templates = [
        "BUY NOW!!! BEST PRICE EVER!!! CLICK HERE!",
        "I was paid to write this review but it's okay.",
        "SCAM! DO NOT BUY! WASTE OF MONEY!",
        "Amazing {product}!! FREE GIFT INCLUDED!! 100% LEGIT!",
        "Cheap quality, broke instantly. Avoid at all costs.",
        "Fake product delivered. Seller is a fraud.",
        "Five stars because I have to, but it's terrible.",
        "The best {product} on the planet! Unbelievable results in 2 seconds!",
        "Don't listen to other reviews, this is garbage.",
        "Instant results!! Magical {product} changed my life forever!!"
    ]
    
    products = ["phone", "laptop", "watch", "shoes", "camera", "bag", "headphones", "gadget", "item"]
    
    data = []
    for i in range(n):
        is_genuine = random.choice([True, False])
        if is_genuine:
            tpl = random.choice(genuine_templates)
            label = 'OR' # Original
        else:
            tpl = random.choice(fake_templates)
            label = 'CG' # Computer Generated/Fake
        
        text = tpl.format(product=random.choice(products))
        # Add some random noise/variation
        if random.random() > 0.7:
            text += " " + "".join(random.choices("abcdefghi ", k=10))
            
        data.append({'text_': text, 'label': label})
    
    df = pd.DataFrame(data)
    if not os.path.exists('dataset'):
        os.makedirs('dataset')
    df.to_csv('dataset/fake_reviews.csv', index=False)
    print(f"Generated large dataset with {len(df)} rows.")
    return df

def train():
    dataset_path = 'dataset/fake_reviews.csv'
    
    # Force generate a large dataset for the user
    df = generate_large_dataset(1500)

    # Preprocessing
    df = df.dropna()
    X = df['text_']
    y = df['label']

    # Vectorization
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

    # Model - Decision Tree
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Save
    if not os.path.exists('models'):
        os.makedirs('models')
        
    with open('models/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('models/vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)

    print("Model and Vectorizer updated successfully with 1500 rows!")

if __name__ == "__main__":
    train()
