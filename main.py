from fastapi import FastAPI, HTTPException, Form, Response
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="WhatsApp Message Sender")

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # Format: whatsapp:+14155238886

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


class MessageRequest(BaseModel):
    to_number: str  # Format: whatsapp:+1234567890
    message: str


@app.get("/")
def read_root():
    return {"message": "WhatsApp Message Sender API", "status": "running"}


@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(), From: str = Form()):
    """
    Receive incoming WhatsApp messages from Twilio
    """
    print(f"Received message from {From}: {Body}")

    # Create response
    resp = MessagingResponse()

    # Send an automatic reply
    resp.message(f"You said: {Body}\n\nThis is an auto-reply from the bot!")

    return Response(content=str(resp), media_type="application/xml")


@app.post("/send-whatsapp")
def send_whatsapp_message(request: MessageRequest):
    """
    Send a WhatsApp message using Twilio
    """
    try:
        message = client.messages.create(
            body=request.message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=request.to_number
        )

        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status,
            "to": request.to_number
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
