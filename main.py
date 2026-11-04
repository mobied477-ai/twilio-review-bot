import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Paste your unique Webhook.site URL here
MOCK_SANDBOX_URL = " https://webhook.site/d7863f8b-1dd5-44d6-8f3d-910aeea69a15
"

@app.route("/send-sms", methods=["POST"])
def send_sms():
    customer_phone = request.form.get("phone")
    shop = request.form.get("shop", "Our Store")
    
    payload = {
        "to": customer_phone,
        "message": f"Thank you for visiting {shop}! How would you rate your service today from 1 to 5?"
    }
    
    # Fires the request straight to your free browser inbox
    response = requests.post(MOCK_SANDBOX_URL, json=payload)
    
    return f"Mock SMS captured! Status Code: {response.status_code}"
