from flask import Flask, render_template, request
import tensorflow as tf
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re

# Initialize Flask app
app = Flask(__name__)

# Load trained model
model = tf.keras.models.load_model("model/url_model.h5")

# Load tokenizer
tokenizer = pickle.load(open("model/tokenizer.pkl", "rb"))

# URL cleaning function
def clean_url(url):
    url = url.lower()
    url = re.sub(r'http\S+', '', url)
    url = re.sub(r'[^a-zA-Z]', ' ', url)
    return url

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    url = request.form['url']

    cleaned = clean_url(url)
    seq = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=100)

    prediction = model.predict(padded)[0][0]

    if prediction > 0.5:
        result = "⚠️ Phishing Website"
    else:
        result = "✅ Safe Website"

    return render_template('index.html', prediction_text=result)

# Run app
if __name__ == "__main__":
    app.run(debug=True)