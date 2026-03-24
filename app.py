from flask import Flask, request, render_template
import pickle
trusted_sites = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "amazon.in",
    "wikipedia.org",
    "microsoft.com",
    "apple.com",
    "github.com",
    "netflix.com"
]

# Load model and vectorizer
model = pickle.load(open("model/url_model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form['url']

    # Step 1: Check trusted sites
    for site in trusted_sites:
        if site in url:
            return render_template('index.html',
                                   prediction_text="✅ Safe Website (Trusted)")

    # Step 2: ML Prediction
    vector = vectorizer.transform([url])
    prediction = model.predict(vector)[0]

    if prediction == 1:
        result = "⚠️ Phishing Website"
    else:
        result = "✅ Safe Website"

    return render_template('index.html', prediction_text=result)

if __name__ == "__main__":
    if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
import os

model = pickle.load(open(os.path.join("model", "url_model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join("model", "vectorizer.pkl"), "rb"))