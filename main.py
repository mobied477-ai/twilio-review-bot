import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TEXTBEE_API_KEY = os.environ.get("TEXTBEE_API_KEY")
TEXTBEE_DEVICE_ID = os.environ.get("TEXTBEE_DEVICE_ID")

@app.route("/send-sms", methods=["POST"])
def send_sms():
    customer_phone = request.form.get("phone")
    shop = request.form.get("shop", "Our Store")
    
    url = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
    headers = {"x-api-key": TEXTBEE_API_KEY}
    payload = {
        "recipients": [customer_phone],
        "message": f"Thank you for visiting {shop}! How would you rate your service today from 1 to 5?"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return f"SMS dispatched via your phone! Status: {response.status_code}"

@app.route("/sms", methods=["POST"])
def inbound_sms():
    # textbee incoming webhook payload structure
    data = request.json or {}
    sender_phone = data.get("sender") or request.form.get("sender", "")
    rating_text = str(data.get("message") or request.form.get("message", "")).strip()
    
    try:
        rating = int(rating_text)
    except ValueError:
        return jsonify({"status": "ignored", "reason": "Not a numeric rating"}), 200

    if rating >= 4:
        reply_message = "Thank you so much! Please consider leaving us a 5-star review on Google: https://g.page/r/your-link"
    else:
        reply_message = "We're sorry your experience wasn't great. Could you reply with what went wrong so we can fix it?"

    # Send the follow-up text back out through your phone
    url = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
    headers = {"x-api-key": TEXTBEE_API_KEY}
    requests.post(url, json={
        "recipients": [sender_phone],
        "message": reply_message
    }, headers=headers)

    return jsonify({"status": "success", "rating": rating}), 200
