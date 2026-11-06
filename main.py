import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TEXTBEE_API_KEY = os.environ.get("TEXTBEE_API_KEY")
TEXTBEE_DEVICE_ID = os.environ.get("TEXTBEE_DEVICE_ID")

# Sultan Grill direct Google Review link
GOOGLE_REVIEW_LINK = "https://reviewthis.biz/autumn-fire-0922"

@app.route("/")
@app.route("/virtual-coffee-shop")
def virtual_shop():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sultan Grill POS</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 25px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h2 { color: #b32400; margin-top: 0; }
            input, button { width: 100%; padding: 12px; margin: 10px 0; box-sizing: border-box; border-radius: 4px; font-size: 16px; }
            input { border: 1px solid #ccc; }
            button { background-color: #b32400; color: white; border: none; font-weight: bold; cursor: pointer; }
            button:hover { background-color: #8b1c00; }
        </style>
    </head>
    <body>
        <h2>🍖 Sultan Grill POS</h2>
        <p>Send a review request SMS to a customer.</p>
        <form action="/send-sms" method="POST">
            <label>Customer Phone Number:</label>
            <input type="text" name="phone" placeholder="+46701234567" required>
            <input type="hidden" name="shop" value="Sultan Grill">
            <button type="submit">Complete Order & Send SMS</button>
        </form>
    </body>
    </html>
    '''

@app.route("/send-sms", methods=["POST"])
def send_sms():
    customer_phone = request.form.get("phone") or (request.get_json(silent=True) or {}).get("phone")
    shop = request.form.get("shop") or (request.get_json(silent=True) or {}).get("shop", "Sultan Grill")
    
    if not customer_phone:
        return jsonify({"error": "Missing phone number"}), 400

    url = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
    headers = {"x-api-key": TEXTBEE_API_KEY}
    
    payload = {
        "recipients": [customer_phone],
        "message": f"Thanks for dining at {shop}! Rate your experience today from 1 to 5 by replying to this text."
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    html_response = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMS Sent Successfully</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 25px; border: 1px solid #ddd; border-radius: 8px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h2 {{ color: #2e7d32; }}
            a {{ display: inline-block; margin-top: 20px; padding: 12px 20px; background-color: #b32400; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; }}
            a:hover {{ background-color: #8b1c00; }}
        </style>
    </head>
    <body>
        <h2>✅ Review Request Sent!</h2>
        <p>The SMS was successfully dispatched to <b>{customer_phone}</b> for <b>{shop}</b>.</p>
        <p style="color: #666; font-size: 14px;">Gateway Status: {response.status_code}</p>
        <a href="/">Send Another Request</a>
    </body>
    </html>
    """
    return html_response, 200

@app.route("/sms", methods=["POST"])
def inbound_sms():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    print("RECEIVED WEBHOOK PAYLOAD:", data)

    nested = data.get("data") or data.get("payload") or {}
    if not isinstance(nested, dict):
        nested = {}

    sender_phone = (
        data.get("sender") 
        or nested.get("sender") 
        or request.form.get("sender", "")
    )
    
    rating_text = str(
        data.get("message") 
        or nested.get("message") 
        or request.form.get("message", "")
    ).strip()

    print(f"Extracted Sender: '{sender_phone}', Message: '{rating_text}'")

    ignored_prefixes = ("Thanks for", "Awesome!", "We're sorry", "Thank you")
    if rating_text.startswith(ignored_prefixes):
        print("Ignored: Outbound bot message echoed by the device.")
        return jsonify({"status": "ignored", "reason": "Outbound echo"}), 200

    try:
        rating = int(rating_text)
    except ValueError:
        print("Ignored: Message is not a clean integer rating.")
        return jsonify({"status": "ignored", "reason": "Not a numeric rating"}), 200

    if rating >= 4:
        reply_message = f"Awesome! Tap here to quickly leave your 5-star review for Sultan Grill on Google: {GOOGLE_REVIEW_LINK}"
    else:
        reply_message = "We're sorry your experience wasn't 5-star. Could you reply with what went wrong so the manager can fix it?"

    if sender_phone:
        url = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
        headers = {"x-api-key": TEXTBEE_API_KEY}
        res = requests.post(url, json={
            "recipients": [sender_phone],
            "message": reply_message
        }, headers=headers)
        print(f"Reply dispatch status: {res.status_code}")

    return jsonify({"status": "success", "rating": rating}), 200
