import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TEXTBEE_API_KEY = os.environ.get("TEXTBEE_API_KEY")
TEXTBEE_DEVICE_ID = os.environ.get("TEXTBEE_DEVICE_ID")

# Sultan Grill direct link
GOOGLE_REVIEW_LINK = "https://maps.app.goo.gl/rRDwKvZkcDvzJLEJ9"

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
            <input type="text" name="phone" placeholder="+1234567890" required>
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
    
    return f'''
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
    ''', 200

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
    ).strip
