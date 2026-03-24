from flask import Flask, render_template, request
import pickle
import os
import re

app = Flask(__name__)

# Load model
model = pickle.load(open(os.path.join("model", "url_model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join("model", "vectorizer.pkl"), "rb"))

# Trusted domains
trusted_domains = [
    "google.com", "youtube.com", "facebook.com",
    "amazon.com", "wikipedia.org", "twitter.com"
]

# URL validation
def is_valid_url(url):
    pattern = re.compile(
        r'^(https?:\/\/)?'
        r'([a-zA-Z0-9\-]+\.)+'
        r'[a-zA-Z]{2,}'
    )
    return re.match(pattern, url)

# Risk scoring
def calculate_risk(url):
    score = 0
    if len(url) > 75:
        score += 2
    if "@" in url:
        score += 3
    if "-" in url:
        score += 1
    if url.count('.') > 3:
        score += 2
    return score

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Predict route
@app.route("/predict", methods=["GET", "POST"])
def predict():

    # If user opens /predict manually
    if request.method == "GET":
        return render_template("index.html", prediction_text="Enter URL to check", confidence="")

    url = request.form["url"].strip().lower()

    # Validate URL
    if not is_valid_url(url):
        return render_template("index.html", prediction_text="❌ Invalid URL", confidence="")

    if not url.startswith("http"):
        url = "http://" + url

    # Trusted domains
    for domain in trusted_domains:
        if domain in url:
            return render_template("index.html", prediction_text="✅ Safe (Trusted)", confidence="100%")

    # Rule-based risk
    risk = calculate_risk(url)
    if risk >= 5:
        return render_template("index.html", prediction_text="⚠️ High Risk Website", confidence="85%")

    # ML Prediction
    data = vectorizer.transform([url])
    prediction = model.predict(data)[0]
    prob = model.predict_proba(data)[0]

    confidence = round(max(prob) * 100, 2)

    if prediction == 1:
        result = "⚠️ Phishing Website"
    else:
        result = "✅ Safe Website"

    return render_template("index.html", prediction_text=result, confidence=f"{confidence}%")

# Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)