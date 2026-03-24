from flask import Flask, render_template, request
import pickle
import os

app = Flask(__name__)

# Load model and vectorizer
model_path = os.path.join("model", "url_model.pkl")
vectorizer_path = os.path.join("model", "vectorizer.pkl")

model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Prediction route
@app.route("/predict", methods=["POST"])
def predict():
    url = request.form["url"]

    # Convert URL to vector
    data = vectorizer.transform([url])

    # Predict
    prediction = model.predict(data)[0]

    if prediction == 1:
        result = "⚠️ Phishing Website"
    else:
        result = "✅ Safe Website"

    return render_template("index.html", prediction_text=result)


# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)