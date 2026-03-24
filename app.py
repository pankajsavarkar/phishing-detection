from flask import Flask, render_template, request
import pickle
import os

app = Flask(__name__)

# Load model
model = pickle.load(open(os.path.join("model", "url_model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join("model", "vectorizer.pkl"), "rb"))

# Trusted domains list
trusted_domains = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "amazon.com",
    "wikipedia.org",
    "twitter.com",
    "instagram.com",
    "linkedin.com"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    url = request.form["url"].lower()

    # 🔹 STEP 1: Trusted domain check
    for domain in trusted_domains:
        if domain in url:
            return render_template(
                "index.html",
                prediction_text="✅ Safe Website (Trusted Domain)"
            )

    # 🔹 STEP 2: ML Prediction
    data = vectorizer.transform([url])
    prediction = model.predict(data)[0]

    # 🔹 STEP 3: Result
    if prediction == 1:
        result = "⚠️ Phishing Website"
    else:
        result = "✅ Safe Website"

    return render_template("index.html", prediction_text=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
LogisticRegression(max_iter=1000, class_weight='balanced')

if len(url) > 75:
    return "⚠️ Suspicious (Very Long URL)"

if "@" in url:
    return "⚠️ Suspicious (Contains @)"