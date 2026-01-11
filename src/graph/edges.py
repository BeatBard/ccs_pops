"""
LangGraph Edges
Conditional routing logic for state transitions
"""

from .state import ConversationState, States
from typing import Literal
import logging

logger = logging.getLogger(__name__)

# Button text mappings (Sinhala - for WhatsApp 3-button limit)
# IMPORTANT: These must match EXACTLY what's in your Twilio Content Templates
# Including multiple variations to handle different template configurations
BUTTON_TEXT_MAP = {
    # ===== GREETING MENU BUTTONS =====
    # Variation 1: Current Twilio template
    "මගේ plan 📋": "show_plan",
    "status 📊": "show_status",
    "check-in ✅": "morning_checkin",
    
    # Variation 2: Full Sinhala
    "මගේ සැලැස්ම 📋": "show_plan",
    "තත්ත්වය 📊": "show_status",
    
    # Variation 3: User's requirement (full Sinhala - long form)
    "මගේ අද දවසේ සැලැස්ම": "show_plan",
    "මගේ වර්තමාන තත්ත්වය": "show_status",
    "උදව් අවශ්‍යයි": "show_help",
    "අද check-in කරන්න": "morning_checkin",

    # ===== PLAN VIEW MENU BUTTONS =====
    "top 3 outlet": "show_top3",
    "ප්‍රමුඛ 3 📍": "show_top3",
    "සම්පූර්ණ ලැයිස්තුව": "show_full_list",
    "නැවත පසුට": "back_to_greeting",
    "ආපසු 🔙": "back_to_greeting",

    # ===== HELP MENU BUTTONS =====
    "දවස පටන් ගන්න 🌅": "morning_checkin",
    "outlet යන්න 📍": "help_visit",
    "outlet visit 📍": "help_visit",
    "විකුණුම් ලියන්න 💰": "help_sales",
    "විකුණුම් record 💰": "help_sales",
    
    # ===== MANUAL TYPING SHORTCUTS =====
    "help": "show_help",
    "උදව්": "show_help",
    "plan": "show_plan",
    "සැලැස්ම": "show_plan",
    "checkin": "morning_checkin",
    "back": "back_to_greeting",
    "ආපසු": "back_to_greeting",
    "top 3": "show_top3",
    "full list": "show_full_list",
}


def route_user_input(state: ConversationState) -> Literal[
    "greeting_menu", "plan_view_menu", "show_outlet_list", "show_status", "help_menu",
    "morning_checkin", "outlet_arrival", "visit_complete", "end_of_day", "error"
]:
    """Route user input to appropriate node based on intent detection"""

    logger.info("=" * 50)
    logger.info("🔀 ROUTING: route_user_input")
    logger.info("=" * 50)

    if not state["messages"]:
        logger.warning("⚠️ No messages in state, routing to greeting_menu")
        return "greeting_menu"

    last_message = state["messages"][-1].content.strip()
    last_message_lower = last_message.lower()
    current_state = state.get("current_state", "IDLE")
    menu_context = state.get("menu_context", "")

    logger.info(f"📝 Last message: '{last_message}'")
    logger.info(f"📊 Current state: {current_state}")
    logger.info(f"🎯 Menu context: {menu_context}")

    # 1. Check for button text responses (exact match, case-insensitive)
    for button_text, action in BUTTON_TEXT_MAP.items():
        if last_message_lower == button_text.lower():
            logger.info(f"🔘 BUTTON DETECTED: '{button_text}' → action: {action}")

            if action == "show_plan":
                return "plan_view_menu"
            elif action == "show_status":
                return "show_status"
            elif action == "show_help":
                return "help_menu"
            elif action == "morning_checkin":
                return "morning_checkin"
            elif action == "show_top3":
                # Update menu_context before routing
                state["menu_context"] = "show_top3"
                return "show_outlet_list"
            elif action == "show_full_list":
                state["menu_context"] = "show_full_list"
                return "show_outlet_list"
            elif action == "back_to_greeting":
                return "greeting_menu"
            elif action in ["help_visit", "help_sales"]:
                # Show specific help then return to greeting
                return "help_menu"

    # 2. Check for numeric input (outlet selection)
    if current_state == States.OUTLET_SELECT:
        if last_message_lower.isdigit():
            number = int(last_message_lower)
            logger.info(f"🔢 NUMERIC INPUT: {number} (outlet selection)")
            # Route to outlet_arrival which will handle the number
            return "outlet_arrival"

    # 3. Greeting keywords → Show greeting menu
    greeting_keywords = ["hi", "hello", "hey", "👋", "හායි", "හෙලෝ"]
    if any(word in last_message_lower for word in greeting_keywords):
        logger.info(f"✅ ROUTE DECISION: greeting_menu (greeting detected)")
        return "greeting_menu"

    # 4. Direct "At SD0001" style messages → outlet arrival
    if "sd" in last_message_lower and any(c.isdigit() for c in last_message):
        logger.info(f"✅ ROUTE DECISION: outlet_arrival (contains 'SD' + digits)")
        return "outlet_arrival"

    if "at " in last_message_lower and any(c.isdigit() for c in last_message):
        logger.info(f"✅ ROUTE DECISION: outlet_arrival (contains 'at' + digit)")
        return "outlet_arrival"

    # 5. Sales recording detection
    if "sales" in last_message_lower or "විකුණුම්" in last_message_lower:
        logger.info(f"✅ ROUTE DECISION: visit_complete (contains 'sales')")
        return "visit_complete"

    # Check if pure number (could be sales value if at outlet)
    if last_message_lower.replace(",", "").replace(".", "").isdigit():
        # If at outlet, treat as sales value
        if state.get("current_outlet"):
            logger.info(f"✅ ROUTE DECISION: visit_complete (numeric sales value)")
            return "visit_complete"

    # 6. End of day detection
    end_keywords = ["end day", "end", "done", "අවසන්", "finish"]
    if any(word in last_message_lower for word in end_keywords):
        logger.info(f"✅ ROUTE DECISION: end_of_day (matched end keyword)")
        return "end_of_day"

    # 7. Default → Show greeting menu (not error)
    logger.info(f"⚠️ ROUTE DECISION: greeting_menu (no pattern matched, showing menu)")
    return "greeting_menu"


def route_after_morning(state: ConversationState) -> Literal["active", "idle"]:
    """Route after morning check-in based on user response"""

    if not state["messages"]:
        return "idle"

    last_message = state["messages"][-1].content.lower()

    # Check button responses
    if last_message in ["ow", "yes", "ඔව්"]:
        return "active"
    elif last_message in ["leave", "na", "නැහැ"]:
        return "idle"

    return "active"  # Default to active


def route_after_visit(state: ConversationState) -> Literal["outlet_arrival", "end_of_day", "active"]:
    """Route after visit completion"""

    if not state["messages"]:
        return "active"

    last_message = state["messages"][-1].content.lower()

    # Check if moving to another outlet
    if "at" in last_message or "sd" in last_message:
        return "outlet_arrival"

    # Check if ending day
    if any(word in last_message for word in ["end day", "end", "done", "අවසන්"]):
        return "end_of_day"

    # Stay active
    return "active"


def should_continue(state: ConversationState) -> Literal["continue", "end"]:
    """Determine if conversation should continue or end"""

    current_state = state.get("current_state", States.IDLE)

    # End conversation after day complete
    if current_state == States.DAY_COMPLETE:
        return "end"

    # End if user explicitly says goodbye
    if state["messages"]:
        last_message = state["messages"][-1].content.lower()
        if any(word in last_message for word in ["goodbye", "bye", "stop", "ගිහින් එන්නම්"]):
            return "end"

    return "continue"
