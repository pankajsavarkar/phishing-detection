from flask import Flask, render_template, request
import pickle
import os
import re

app = Flask(__name__)

# =========================
# Load model and vectorizer
# =========================
model = pickle.load(open(os.path.join("model", "url_model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join("model", "vectorizer.pkl"), "rb"))

# =========================
# Trusted domains (safe list)
# =========================
trusted_domains = [
    "google.com", "youtube.com", "facebook.com",
    "amazon.com", "wikipedia.org", "twitter.com",
    "instagram.com", "linkedin.com"
]

# =========================
# URL validation function
# =========================
def is_valid_url(url):
    pattern = re.compile(
        r'^(https?:\/\/)?'          # http:// or https://
        r'([a-zA-Z0-9\-]+\.)+'      # domain name
        r'[a-zA-Z]{2,}'             # extension
    )
    return re.match(pattern, url)

# =========================
# Home route
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# Prediction route
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    url = request.form["url"].strip().lower()

    # 🚨 Step 1: Validate URL
    if not is_valid_url(url):
        return render_template(
            "index.html",
            prediction_text="❌ Invalid URL (Enter proper website link)"
        )

    # 🔹 Step 2: Auto add http if missing
    if not url.startswith("http"):
        url = "http://" + url

    # 🔹 Step 3: Trusted domain check
    for domain in trusted_domains:
        if domain in url:
            return render_template(
                "index.html",
                prediction_text="✅ Safe Website (Trusted Domain)"
            )

    # 🔹 Step 4: Suspicious checks
    if len(url) > 75:
        return render_template(
            "index.html",
            prediction_text="⚠️ Suspicious (Very Long URL)"
        )

    if "@" in url:
        return render_template(
            "index.html",
            prediction_text="⚠️ Suspicious (Contains @)"
        )

    if "-" in url:
        return render_template(
            "index.html",
            prediction_text="⚠️ Suspicious (Hyphen detected)"
        )

    # 🔹 Step 5: ML Prediction
    data = vectorizer.transform([url])
    prediction = model.predict(data)[0]

    # 🔹 Step 6: Result
    if prediction == 1:
        result = "⚠️ Phishing Website"
    else:
        result = "✅ Safe Website"

    return render_template("index.html", prediction_text=result)

# =========================
# Run app
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)