import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Load credentials from Render Environment Variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/send-sms", methods=["POST"])
def send_sms():
    customer_phone = request.form.get("phone")
    shop = request.form.get("shop", "Our Store")
    
    message = client.messages.create(
        body=f"Thank you for visiting {shop}! How would you rate your service today from 1 to 5?",
        from_=TWILIO_NUMBER,
        to=customer_phone
    )
    return f"Live SMS sent! SID: {message.sid}"

@app.route("/sms", methods=["POST"])
def inbound_sms():
    rating_text = request.form.get("Body", "").strip()
    resp = MessagingResponse()
    
    try:
        rating = int(rating_text)
    except ValueError:
        resp.message("Please reply with a number from 1 to 5.")
        return str(resp)

    if rating >= 4:
        resp.message("Thank you so much! Please consider leaving us a 5-star review on Google: https://g.page/r/your-link")
    else:
        resp.message("We're sorry your experience wasn't great. Could you reply with what went wrong so we can fix it?")

    # Return TwiML XML response so Twilio automatically sends the SMS back to the customer
    return str(resp)
