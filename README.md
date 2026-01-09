# Twilio WhatsApp Reaction Bot

A simple FastAPI backend that receives WhatsApp messages via Twilio and sends emoji reactions.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Twilio credentials in `.env`:
- Add your `TWILIO_ACCOUNT_SID`
- Add your `TWILIO_AUTH_TOKEN`
- Add your `TWILIO_WHATSAPP_NUMBER` (e.g., `whatsapp:+14155238886`)

3. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

4. Expose your local server using ngrok:
```bash
ngrok http 8000
```

5. Configure Twilio webhook:
- Go to your Twilio Console
- Navigate to WhatsApp Sandbox Settings
- Set the webhook URL to: `https://your-ngrok-url.ngrok.io/webhook`

## How it works

When a user sends a WhatsApp message to your Twilio number:
1. Twilio forwards the message to your `/webhook` endpoint
2. The backend receives the message and sends back a 👍 reaction
3. You can change the emoji in `main.py` (line 42)

## Available Endpoints

- `GET /` - Health check
- `POST /webhook` - Twilio webhook endpoint
