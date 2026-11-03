import os
from flask import Flask, request
from twilio.rest import Client

app = Flask(__name__)

# Load Twilio credentials from your Render environment variables
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route("/")
def home():
    return "Twilio Review Bot is running!"

@app.route("/send-sms", methods=["POST"])
def send_sms():
    customer_phone = request.form.get("phone")
    
    message = client.messages.create(
        body="Your Appt is coming up on-",
        from_=TWILIO_NUMBER,
        to=customer_phone
    )
    return f"Message sent! SID: {message.sid}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
