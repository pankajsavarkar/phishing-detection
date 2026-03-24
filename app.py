from flask import Flask, render_template, request
import pickle
import os
import re

app = Flask(__name__)

# Load model
model = pickle.load(open(os.path.join("model", "url_model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join("model", "vectorizer.pkl"), "rb"))

# History
history = []

# 100+ Trusted Domains
trusted_domains = [
"google.com","youtube.com","facebook.com","amazon.com","wikipedia.org","twitter.com",
"instagram.com","linkedin.com","microsoft.com","apple.com","github.com","stackoverflow.com",
"netflix.com","yahoo.com","bing.com","reddit.com","whatsapp.com","telegram.org","zoom.us",
"office.com","live.com","outlook.com","dropbox.com","adobe.com","canva.com","spotify.com",
"quora.com","medium.com","wordpress.com","blogger.com","nytimes.com","bbc.com","cnn.com",
"forbes.com","economist.com","huffpost.com","theguardian.com","aljazeera.com","espn.com",
"fifa.com","nba.com","olympics.com","paypal.com","stripe.com","visa.com","mastercard.com",
"icici.com","hdfcbank.com","sbi.co.in","axisbank.com","kotak.com","bankofbaroda.in",
"airbnb.com","booking.com","expedia.com","tripadvisor.com","makemytrip.com","irctc.co.in",
"flipkart.com","snapdeal.com","myntra.com","ajio.com","tatacliq.com",
"coursera.org","udemy.com","edx.org","khanacademy.org","byjus.com","unacademy.com",
"mit.edu","stanford.edu","harvard.edu","ox.ac.uk","cam.ac.uk",
"nasa.gov","who.int","un.org","worldbank.org","imf.org",
"pinterest.com","tumblr.com","flickr.com","imgur.com",
"mozilla.org","ubuntu.com","linux.org","oracle.com","ibm.com","intel.com",
"nvidia.com","amd.com","dell.com","hp.com","lenovo.com",
"samsung.com","xiaomi.com","oneplus.com","oppo.com","vivo.com"
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

# Home (reset history)
@app.route("/")
def home():
    global history
    history.clear()
    return render_template("index.html", history=history)

# Predict
@app.route("/predict", methods=["POST"])
def predict():
    global history

    url = request.form["url"].strip().lower()

    if not is_valid_url(url):
        result = "❌ Invalid URL"
        confidence = ""
    else:
        if not url.startswith("http"):
            url = "http://" + url

        if any(domain in url for domain in trusted_domains):
            result = "✅ Safe (Trusted)"
            confidence = "100%"
        else:
            risk = calculate_risk(url)

            if risk >= 5:
                result = "⚠️ Suspicious Website"
                confidence = "85%"
            else:
                data = vectorizer.transform([url])
                prediction = model.predict(data)[0]
                prob = model.predict_proba(data)[0]

                confidence = str(round(max(prob) * 100, 2)) + "%"

                if prediction == 1:
                    result = "⚠️ Phishing Website"
                else:
                    result = "✅ Safe Website"

    history.insert(0, {
        "url": url,
        "result": result,
        "confidence": confidence
    })

    if len(history) > 10:
        history.pop()

    return render_template("index.html",
                           prediction_text=result,
                           confidence=confidence,
                           history=history)

# Dashboard
@app.route("/dashboard")
def dashboard():
    safe = sum(1 for item in history if "Safe" in item["result"])
    phishing = sum(1 for item in history if "Phishing" in item["result"])
    suspicious = sum(1 for item in history if "Suspicious" in item["result"])

    return render_template("dashboard.html",
                           safe=safe,
                           phishing=phishing,
                           suspicious=suspicious)

if __name__ == "__main__":
    app.run(debug=True)