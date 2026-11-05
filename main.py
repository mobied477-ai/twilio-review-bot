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

    # Ignore our own outbound review requests echoed by the Android device
    if rating_text.startswith("Thank you for visiting") or rating_text.startswith("Thank you so much") or rating_text.startswith("We're sorry"):
        print("Ignored: Outbound bot message echoed by the device.")
        return jsonify({"status": "ignored", "reason": "Outbound echo"}), 200

    try:
        rating = int(rating_text)
    except ValueError:
        print("Ignored: Message is not a clean integer rating.")
        return jsonify({"status": "ignored", "reason": "Not a numeric rating"}), 200

    if rating >= 4:
        reply_message = "Thank you so much! Please consider leaving us a 5-star review on Google: https://g.page/r/your-link"
    else:
        reply_message = "We're sorry your experience wasn't great. Could you reply with what went wrong so we can fix it?"

    if sender_phone:
        url = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
        headers = {"x-api-key": TEXTBEE_API_KEY}
        res = requests.post(url, json={
            "recipients": [sender_phone],
            "message": reply_message
        }, headers=headers)
        print(f"Reply dispatch status: {res.status_code}")

    return jsonify({"status": "success", "rating": rating}), 200
