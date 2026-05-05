from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle as pkl
import numpy as np
import nltk
from nltk.corpus import stopwords
import re

# SETUP
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

model = load_model("model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pkl.load(f)

MAX_LEN = 100

# PREPROCESSING
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s0-9]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return ' '.join(words)

# SENTIMENT
def predict_sentiment(text):
    clean_text = preprocess_text(text)
    words = clean_text.split()

    # Positive keywords
    if any(w in words for w in ["good", "great", "excellent", "amazing", "nice", "satisfied", "well","helpful"]):
        return "positive", clean_text

    # Negative keywords
    if any(w in words for w in ["bad", "worst", "terrible", "rude"]):
        return "negative", clean_text

    sequence = tokenizer.texts_to_sequences([clean_text])
    padded = pad_sequences(sequence, maxlen=MAX_LEN, padding='post')

    prediction = model.predict(padded, verbose=0)[0]

    # Neutral (if model not confident)
    if max(prediction) < 0.6:
        return "neutral", clean_text

    labels = ['negative', 'neutral', 'positive']
    sentiment = labels[np.argmax(prediction)]

    return sentiment, clean_text

# CATEGORY
def get_categories(words):
    categories = []

    if any(w in words for w in ["baggage", "luggage", "bag"]):
        categories.append("Baggage Handling Issue")

    if any(w in words for w in ["delay", "late", "delayed"]):
        categories.append("Flight Delay Issue")

    if any(w in words for w in ["cancel", "cancelled"]):
        categories.append("Flight Cancellation")

    if any(w in words for w in ["staff", "rude", "crew", "service"]):
        categories.append("Customer Service Issue")

    if any(w in words for w in ["seat", "comfort", "food"]):
        categories.append("Comfort Issue")

    return categories if categories else ["General Feedback"]

def choose_primary_category(categories):
    priority_order = [
        "Flight Cancellation",
        "Flight Delay Issue",
        "Baggage Handling Issue",
        "Customer Service Issue",
        "Comfort Issue",
        "General Feedback"
    ]
    return sorted(categories, key=lambda x: priority_order.index(x))[0]

# SEVERITY
def get_severity(words, category, text):
    high_words = ["lost", "worst", "terrible", "refund", "complaint"]
    medium_words = ["issue", "problem", "bad", "rude"]

    # High words
    if any(w in words for w in high_words):
        return "High"

    # Delay handling (minutes + hours)
    if category == "Flight Delay Issue":

        match_min = re.search(r'(\d+)\s*minutes?', text)
        if match_min:
            minutes = int(match_min.group(1))
            if minutes <= 15:
                return "Low"
            elif minutes <= 60:
                return "Medium"
            else:
                return "High"

        match_hr = re.search(r'(\d+)\s*hours?', text)
        if match_hr:
            hours = int(match_hr.group(1))
            if hours == 1:
                return "Medium"
            else:
                return "High"

        return "Medium"

    # Medium words
    if any(w in words for w in medium_words):
        return "Medium"

    return "Low"

# URGENCY
def get_priority(sentiment, severity, category):

    if severity == "High":
        return "High"

    if severity == "Medium":
        return "Medium"

    if sentiment == "negative":
        return "Medium"

    return "Low"

# MAIN FUNCTION
def analyze_text(text):
    sentiment, clean_text = predict_sentiment(text)
    words = clean_text.split()

    categories = get_categories(words)
    category = choose_primary_category(categories)
    category_text = category.lower()

    #Critical rule: cancellation
    if category == "Flight Cancellation":
        sentiment = "negative"
        severity = "High"
    else:
        severity = get_severity(words, category, text)

    urgency = get_priority(sentiment, severity, category)

    # INSIGHT
    if sentiment == "negative":
        insight = f"The customer is facing a {category_text}, which may reduce satisfaction."
    elif sentiment == "positive":
        insight = f"The customer had a positive experience related to {category_text}."
    else:
        insight = f"The feedback is neutral regarding {category_text}."

    # RECOMMENDATION
    if category == "Baggage Handling Issue":
        recommendation = "Improve baggage tracking and reduce delays."
    elif category == "Flight Delay Issue":
        recommendation = "Enhance scheduling and provide real-time updates."
    elif category == "Flight Cancellation":
        recommendation = "Ensure timely communication and compensation."
    elif category == "Customer Service Issue":
        recommendation = "Improve staff training and customer interaction."
    elif category == "Comfort Issue":
        recommendation = "Improve seating, food, and onboard comfort."
    else:
        recommendation = "Maintain service quality and monitor feedback."

    return {
        "urgency": urgency,
        "sentiment": sentiment,
        "category": category,
        "severity": severity,
        "insight": insight,
        "recommendation": recommendation
    }

# TEST
# if __name__ == "__main__":
#     tests = [
#         "Boarding started at 5pm",
#         "Food was bad",
#         "Flight delayed by 10 minutes",
#         "Flight delayed by 45 minutes",
#         "Flight delayed by 2 hours",
#         "Flight cancelled without notice",
#         "Amazing service, very satisfied",
#         "Flight delayed but staff handled it well"
#     ]

#     for t in tests:
#         print("\nInput:", t)
#         print(analyze_text(t))