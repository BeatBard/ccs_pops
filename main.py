"""
DSR Sales Coaching Assistant - Main Application
================================================

A WhatsApp-based sales coaching assistant for Distribution Sales Representatives (DSRs).
Built with FastAPI, LangGraph, and Twilio WhatsApp API.

Key Features:
- Morning check-in with daily plan
- Real-time outlet coaching with LIPB tracking
- Sales recording and progress tracking
- End-of-day performance summary

Author: CCS Team
"""

# =============================================================================
# IMPORTS
# =============================================================================
from fastapi import FastAPI, HTTPException, Form, Response, BackgroundTasks
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
from dotenv import load_dotenv
import logging
from datetime import datetime

# Local imports
from src.graph.workflow import compiled_workflow
from src.graph.state import create_initial_state
from src.core.constants import States
from src.whatsapp import get_template, TemplateType

# =============================================================================
# CONFIGURATION
# =============================================================================
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Set module-specific log levels for debugging
logging.getLogger("src.graph.workflow").setLevel(logging.DEBUG)
logging.getLogger("src.handlers").setLevel(logging.DEBUG)
logging.getLogger("src.core").setLevel(logging.DEBUG)

# =============================================================================
# TWILIO CONFIGURATION
# =============================================================================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # Format: whatsapp:+14155238886
USE_CONTENT_TEMPLATES = os.getenv("USE_CONTENT_TEMPLATES", "true").lower() == "true"

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# =============================================================================
# SESSION MANAGEMENT
# =============================================================================
# In-memory session store (for POC - use Redis/DB in production)
user_sessions: dict = {}

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================
app = FastAPI(
    title="DSR Sales Coaching Assistant",
    description="WhatsApp-based sales coaching for DSRs",
    version="1.0.0"
)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================
class MessageRequest(BaseModel):
    """Request model for sending WhatsApp messages"""
    to_number: str  # Format: whatsapp:+1234567890
    message: str


# =============================================================================
# WHATSAPP MESSAGING FUNCTIONS
# =============================================================================
def send_whatsapp_with_template(to_number: str, message: str, template_type: str = None) -> str:
    """
    Send WhatsApp message using Twilio Content Templates.
    
    Args:
        to_number: WhatsApp number (format: whatsapp:+1234567890)
        message: Dynamic message content for the template variable {{1}}
        template_type: Template type ('greeting', 'plan_view', 'help')
    
    Returns:
        Message SID if successful, None otherwise
    
    Note:
        - Content Templates must be created in Twilio Console first
        - WhatsApp allows MAX 3 buttons for unapproved session templates
        - Message content must NOT have: excessive emojis, double newlines
        - Error 63013 = policy violation from bad content format
    """
    try:
        content_sid = None
        
        # Get Content SID from template configuration
        if template_type and USE_CONTENT_TEMPLATES:
            template = get_template(TemplateType(template_type))
            if template and template.content_sid:
                content_sid = template.content_sid
                logger.info(f"📤 Using Content Template: {template_type} (SID: {content_sid[:10]}...)")
            else:
                logger.warning(f"⚠️ No Content SID found for template: {template_type}")

        # Send with Content Template if available
        if content_sid:
            return _send_with_template(to_number, message, content_sid)
        
        # Fallback: Send as plain text
        return _send_plain_text(to_number, message, template_type)

    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return None


def _send_with_template(to_number: str, message: str, content_sid: str) -> str:
    """Send message using Twilio Content Template."""
    try:
        # Content variables must be JSON string with keys matching template {{1}}, {{2}}, etc.
        content_vars_json = json.dumps({"1": message})
        logger.info(f"📤 Content SID: {content_sid}")
        logger.info(f"📤 Template variables: {content_vars_json}")
        logger.info(f"📤 From: {TWILIO_WHATSAPP_NUMBER}")
        logger.info(f"📤 To: {to_number}")

        msg = client.messages.create(
            content_sid=content_sid,
            content_variables=content_vars_json,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )

        _log_message_response(msg, "Content Template", to_number)
        return msg.sid
        
    except Exception as e:
        logger.warning(f"⚠️ Content Template failed: {e}")
        logger.warning(f"   Falling back to plain text")
        return None


def _send_plain_text(to_number: str, message: str, template_type: str = None) -> str:
    """Send plain text message with optional text-based button hints."""
    logger.info(f"📤 Sending as PLAIN TEXT (no template)")
    
    # Add text-based button hints based on template type
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
    
    _log_message_response(msg, "Plain text", to_number)
    return msg.sid


def _log_message_response(msg, message_type: str, to_number: str):
    """Log Twilio message response details."""
    logger.info(f"✅ Sent {message_type} message to {to_number}")
    logger.info(f"   Message SID: {msg.sid}")
    logger.info(f"   Status: {msg.status}")
    logger.info(f"   Direction: {msg.direction}")
    
    if hasattr(msg, 'error_code') and msg.error_code:
        logger.error(f"   Error code: {msg.error_code}")
        logger.error(f"   Error message: {msg.error_message}")


# =============================================================================
# MESSAGE PROCESSING
# =============================================================================
def process_message_async(phone_number: str, message_body: str):
    """
    Process incoming WhatsApp message through LangGraph.

    This function runs in the background to avoid blocking the webhook response.

    Args:
        phone_number: User's WhatsApp number
        message_body: Content of the incoming message
    """
    try:
        # Get or create session
        if phone_number not in user_sessions:
            # Create initial state with default DSR name (in production, lookup from DB)
            user_sessions[phone_number] = create_initial_state(
                dsr_name="Nalin Perera",
                target_date=datetime.now()
            )
            logger.info(f"✨ Created new session for {phone_number}")

        # Get current state
        state = user_sessions[phone_number]

        # Parse message for button action or text
        button_action = None
        # Check if message is a button action (from Twilio button clicks)
        # Twilio sends button actions in UPPERCASE, convert to match ButtonAction enum (lowercase)
        message_upper = message_body.strip().upper()
        if message_upper in ["CHECKIN", "AREA_VIEW", "OUTLET_DETAILS", "END_SUMMARY", "BACK"]:
            # Convert to lowercase to match ButtonAction enum values
            button_action = message_upper
            logger.info(f"   ├── Button detected: {message_upper}")

        # Update state with user message and button action
        state["user_message"] = message_body
        state["button_action"] = button_action

        logger.info(f"📩 Processing: '{message_body}' (button: {button_action})")

        # Invoke LangGraph with checkpointing config
        config = {"configurable": {"thread_id": phone_number}}
        result = compiled_workflow.invoke(state, config)

        # Update session with new state
        user_sessions[phone_number] = result

        # Send AI response back to user
        response_message = result.get("response_message", "")
        response_messages = result.get("response_messages", [])
        template_type = result.get("template_type", "text")

        # Handle multiple messages (for outlet details with coaching)
        if response_messages:
            logger.info(f"📱 Sending {len(response_messages)} separate messages with template: {template_type}")
            for i, msg in enumerate(response_messages, 1):
                logger.info(f"   └── Message {i}/{len(response_messages)}")
                send_whatsapp_with_template(phone_number, msg, template_type)
            logger.info(f"✅ Processed message for {phone_number}, state: {result.get('current_state', 'UNKNOWN')}")
        elif response_message:
            logger.info(f"📱 Sending response with template: {template_type}")
            send_whatsapp_with_template(phone_number, response_message, template_type)
            logger.info(f"✅ Processed message for {phone_number}, state: {result.get('current_state', 'UNKNOWN')}")
        else:
            logger.warning(f"⚠️ No response message generated for {phone_number}")

    except Exception as e:
        logger.error(f"❌ Error processing message: {e}", exc_info=True)
        error_msg = "සමාවෙන්න, දෝෂයක් සිදු විය. කරුණාකර නැවත උත්සාහ කරන්න."
        send_whatsapp_with_template(phone_number, error_msg)


# =============================================================================
# API ENDPOINTS
# =============================================================================
@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "message": "DSR Sales Coaching Assistant",
        "status": "running",
        "active_sessions": len(user_sessions)
    }


@app.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(),
    From: str = Form()
):
    """
    Twilio webhook endpoint for incoming WhatsApp messages.
    
    Messages are processed in the background to return a quick response
    to Twilio (avoiding timeout issues).
    """
    logger.info(f"Received message from {From}: {Body}")

    # Process message in background
    background_tasks.add_task(process_message_async, From, Body)

    # Return empty TwiML response immediately
    resp = MessagingResponse()
    return Response(content=str(resp), media_type="application/xml")


@app.post("/send-whatsapp")
def send_whatsapp_message(request: MessageRequest):
    """
    Manual endpoint to send a WhatsApp message.
    
    Useful for testing and administrative purposes.
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


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
