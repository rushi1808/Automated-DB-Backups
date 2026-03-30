import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

from utils.logger import setup_logger

logger = setup_logger("data_classifier")

# Minimal dummy dataset for predicting Data Sensitivity
# 1 = Sensitive (Contains passwords, keys, PII), 0 = Safe
TRAINING_DATA = [
    # Safe Text
    ("This is a daily report on server uptime.", 0),
    ("Hello team, the meeting is scheduled for 3 PM.", 0),
    ("The total revenue for Q3 was 1.5 million dollars.", 0),
    ("Grocery list: apples, milk, bread, eggs.", 0),
    ("Please follow up with the client regarding their feedback.", 0),
    ("User guide documentation for the new software release.", 0),
    ("The quick brown fox jumps over the lazy dog.", 0),
    
    # Sensitive Text
    ("My bank account password is Password123!", 1),
    ("AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE", 1),
    ("Here are the credit card details: 4111-2222-3333-4444 CVV 123", 1),
    ("SSN: 123-45-6789", 1),
    ("Database connection string: mysql://root:supersecret@localhost:3306/db", 1),
    ("SSH private key follows: -----BEGIN RSA PRIVATE KEY-----", 1),
    ("The admin login credentials are admin:adminpassword", 1)
]

# Train the simple ML model globally so it only trains once at startup
texts = [x[0] for x in TRAINING_DATA]
labels = [x[1] for x in TRAINING_DATA]

logger.info("Training ML Data Classification Model (Tfidf + Naive Bayes)...")
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(texts, labels)
logger.info("ML Data Classification Model ready.")

def predict_sensitivity(text_content):
    """
    Takes string content from a file and predicts if it contains sensitive data.
    Returns: bool (True if Sensitive, False if Safe)
    """
    if not text_content or len(text_content.strip()) == 0:
        return False
        
    # We take the first 1000 characters to make a quick prediction
    sample_text = text_content[:1000]
    
    prediction = model.predict([sample_text])[0]
    is_sensitive = bool(prediction == 1)
    
    logger.info(f"ML Prediction for snippet: Sensitive={is_sensitive}")
    return is_sensitive
