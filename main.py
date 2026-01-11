from fastapi import FastAPI, HTTPException, Form, Response, BackgroundTasks
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from langchain_core.messages import HumanMessage
import os
import json
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import LangGraph components
from src.graph import graph_app, create_initial_state, States

# Import WhatsApp button templates
from src.whatsapp import get_template, TemplateType

# Load environment variables
load_dotenv()

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Set logging levels for different modules
logging.getLogger("src.graph.nodes").setLevel(logging.DEBUG)
logging.getLogger("src.graph.edges").setLevel(logging.DEBUG)
logging.getLogger("src.tools").setLevel(logging.DEBUG)

app = FastAPI(title="DSR Sales Coaching Assistant")

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # Format: whatsapp:+14155238886

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# In-memory session store (for POC - use Redis/DB in production)
user_sessions = {}


class MessageRequest(BaseModel):
    to_number: str  # Format: whatsapp:+1234567890
    message: str


@app.get("/")
def read_root():
    return {
        "message": "DSR Sales Coaching Assistant",
        "status": "running",
        "active_sessions": len(user_sessions)
    }


def send_whatsapp_with_template(to_number: str, message: str, template_type: str = None):
    """
    Send WhatsApp message using Twilio Content Templates

    Args:
        to_number: WhatsApp number (format: whatsapp:+1234567890)
        message: Dynamic message content
        template_type: Template type (greeting, plan_view, help)

    Content Templates must be created in Twilio Console first.
    See src/whatsapp/templates.py for instructions.
    """
    # Content Templates work in Sandbox for Quick Reply buttons within 24hr session
    # BUT message content must NOT have: emojis, double newlines, or >4 consecutive spaces
    # Error 63013 = policy violation from bad content format
    USE_TEMPLATES = os.getenv("USE_CONTENT_TEMPLATES", "true").lower() == "true"
    
    try:
        # Get Content SID from template configuration
        content_sid = None
        if template_type and USE_TEMPLATES:
            template = get_template(TemplateType(template_type))
            if template and template.content_sid:
                content_sid = template.content_sid
                logger.info(f"📤 Using Content Template: {template_type} (SID: {content_sid[:10]}...)")
            else:
                logger.warning(f"⚠️ No Content SID found for template: {template_type}")

        # Send with Content Template if available
        if content_sid:
            try:
                content_vars = {"1": message}
                logger.info(f"📤 Template variables: {json.dumps(content_vars)}")

                msg = client.messages.create(
                    content_sid=content_sid,
                    content_variables=json.dumps(content_vars),
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=to_number
                )

                # Log detailed response
                logger.info(f"✅ Sent with Content Template to {to_number}")
                logger.info(f"   Message SID: {msg.sid}")
                logger.info(f"   Status: {msg.status}")
                logger.info(f"   Direction: {msg.direction}")
                logger.info(f"   Date created: {msg.date_created}")
                if hasattr(msg, 'error_code') and msg.error_code:
                    logger.error(f"   Error code: {msg.error_code}")
                    logger.error(f"   Error message: {msg.error_message}")

                return msg.sid
            except Exception as e:
                logger.warning(f"⚠️ Content Template failed: {e}, falling back to plain text")

        # Fallback: Send as plain text with text-based buttons
        logger.info(f"📤 Sending as PLAIN TEXT (no template)")
        
        # Add text-based button hints for greeting
        if template_type == "greeting":
            message += "\n\n📱 *Reply with:*\n"
            message += "• \"1\" - මගේ අද දවසේ සැලැස්ම\n"
            message += "• \"2\" - මගේ වර්තමාන තත්ත්වය\n"
            message += "• \"3\" - උදව් අවශ්‍යයි\n"
            message += "• \"4\" - අද Check-in කරන්න"
        elif template_type == "plan_view":
            message += "\n\n📱 *Reply with:*\n"
            message += "• \"1\" - Top 3 Outlet\n"
            message += "• \"2\" - සම්පූර්ණ ලැයිස්තුව\n"
            message += "• \"3\" - නැවත පසුට"
        
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
        logger.info(f"✅ Sent plain message to {to_number}")
        logger.info(f"   Message SID: {msg.sid}")
        logger.info(f"   Status: {msg.status}")
        logger.info(f"   Direction: {msg.direction}")
        if hasattr(msg, 'error_code') and msg.error_code:
            logger.error(f"   Error code: {msg.error_code}")
            logger.error(f"   Error message: {msg.error_message}")
        return msg.sid

    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return None


def process_message_async(phone_number: str, message_body: str):
    """Process message through LangGraph in background"""
    try:
        # Get or create session
        if phone_number not in user_sessions:
            user_sessions[phone_number] = create_initial_state(phone_number)
            logger.info(f"Created new session for {phone_number}")

        # Get current state
        state = user_sessions[phone_number]

        # Add user message to state
        state["messages"].append(HumanMessage(content=message_body))
        state["updated_at"] = datetime.now().isoformat()

        # Invoke graph with config for checkpointing
        config = {"configurable": {"thread_id": phone_number}}
        result = graph_app.invoke(state, config)

        # Update session with new state
        user_sessions[phone_number] = result

        # Get AI response (last message)
        if result["messages"]:
            ai_response = result["messages"][-1].content
            template_type = result.get("template_type")  # Get from state

            logger.info(f"📱 Sending response with template: {template_type or 'None (plain text)'}")

            # Send response back to user with appropriate template
            send_whatsapp_with_template(phone_number, ai_response, template_type)

            logger.info(f"✅ Processed message for {phone_number}, state: {result['current_state']}")

    except Exception as e:
        logger.error(f"❌ Error processing message: {e}", exc_info=True)
        # Send error message
        error_msg = "සමාවෙන්න, දෝෂයක් සිදු විය. කරුණාකර නැවත උත්සාහ කරන්න."
        send_whatsapp_with_template(phone_number, error_msg)


@app.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(),
    From: str = Form()
):
    """
    Receive incoming WhatsApp messages from Twilio webhook
    """
    logger.info(f"Received message from {From}: {Body}")

    # Send processing indicator immediately
    resp = MessagingResponse()

    # Process message in background
    background_tasks.add_task(process_message_async, From, Body)

    # Return empty TwiML response immediately
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
