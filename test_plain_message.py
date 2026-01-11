"""Quick test to send plain WhatsApp message without Content Template"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Test plain message
msg = client.messages.create(
    body="සුභ උදෑසනක්! This is a test message from your bot.",
    from_=TWILIO_WHATSAPP_NUMBER,
    to="whatsapp:+94772057878"
)

print(f"Message SID: {msg.sid}")
print(f"Status: {msg.status}")
print(f"Direction: {msg.direction}")
print(f"Date created: {msg.date_created}")

# Fetch updated status
import time
time.sleep(2)
updated_msg = client.messages(msg.sid).fetch()
print(f"\nUpdated status after 2 seconds: {updated_msg.status}")
if hasattr(updated_msg, 'error_code') and updated_msg.error_code:
    print(f"Error code: {updated_msg.error_code}")
    print(f"Error message: {updated_msg.error_message}")
