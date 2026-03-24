from flask import Flask, render_template, request
import pickle
import os

app = Flask(__name__)

# Load model
model = pickle.load(open(os.path.join("model", "url_model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join("model", "vectorizer.pkl"), "rb"))

# Trusted domains
trusted_domains = [
    "google.com", "youtube.com", "facebook.com",
    "amazon.com", "wikipedia.org"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    url = request.form["url"].lower()

    # ✅ Rule 1: Trusted domains
    for domain in trusted_domains:
        if domain in url:
            return render_template(
                "index.html",
                prediction_text="✅ Safe Website (Trusted Domain)"
            )

    # ✅ Rule 2: Suspicious checks
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

    # ✅ ML Prediction
    data = vectorizer.transform([url])
    prediction = model.predict(data)[0]

    if prediction == 1:
        result = "⚠️ Phishing Website"
    else:
        result = "✅ Safe Website"

    return render_template("index.html", prediction_text=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)