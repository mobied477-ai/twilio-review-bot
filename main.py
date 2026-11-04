import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Free Webhook.site URL for outgoing mock response inspection
MOCK_SANDBOX_URL = "https://webhook.site/d7863f8b-1dd5-44d6-8f3d-910aeea69a15"

@app.route("/send-sms", methods=["POST"])
def send_sms():
    customer_phone = request.form.get("phone")
    shop = request.form.get("shop", "Our Store")
    
    payload = {
        "to": customer_phone,
        "message": f"Thank you for visiting {shop}! How would you rate your service today from 1 to 5?"
    }
    
    response = requests.post(MOCK_SANDBOX_URL, json=payload)
    return f"Mock SMS captured! Status Code: {response.status_code}"

@app.route("/sms", methods=["POST"])
def inbound_sms():
    sender_phone = request.form.get("From")
    rating_text = request.form.get("Body", "").strip()
    
    # Try parsing the rating integer
    try:
        rating = int(rating_text)
    except ValueError:
        response_msg = "Please reply with a number from 1 to 5."
        return response_msg, 200

    # Smart Routing Logic
    if rating >= 4:
        response_msg = "Thank you so much! Please consider leaving us a 5-star review on Google: https://g.page/r/your-google-review-link"
    else:
        response_msg = "We're sorry your experience wasn't great. Could you reply with what went wrong so we can fix it?"

    # Send the automated follow-up response back to your mock Webhook sandbox
    requests.post(MOCK_SANDBOX_URL, json={
        "to": sender_phone,
        "reply_message": response_msg
    })
    
    return f"Processed rating: {rating}. Follow-up sent!", 200
