from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# REPLACE THIS WITH YOUR REAL GOOGLE REVIEW LINK
GOOGLE_REVIEW_LINK = "https://g.page/r/YOUR_GOOGLE_BUSINESS_LINK/review"

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()

    if incoming_msg in ['4', '5']:
        resp.message(
            f"Thank you so much for your support! Please take 10 seconds to share your experience on Google: {GOOGLE_REVIEW_LINK}"
        )
    elif incoming_msg in ['1', '2', '3']:
        resp.message(
            "We are so sorry your experience wasn't perfect. Please reply with what went wrong so our management team can make it right privately."
        )
    else:
        resp.message(
            "Thanks for reaching out! Reply with a rating from 1 to 5 to let us know how we did today."
        )

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)