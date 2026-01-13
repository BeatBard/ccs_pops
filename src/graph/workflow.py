"""
LangGraph Workflow - Clean Architecture
========================================

Main workflow implementation using LangGraph StateGraph.
Integrates with the clean architecture handlers for business logic.

Following LangGraph 2026 best practices:
- StateGraph with TypedDict
- Pure functions as nodes returning partial state updates
- Conditional edges for routing
- Layered error handling
- MemorySaver checkpointer for POC (Postgres for production)
"""

import logging
from datetime import datetime, date
from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ConversationState
from ..core.constants import States, Intent, ButtonAction
from ..core.intent_classifier import intent_classifier
from ..handlers.greeting_handler import greeting_handler
from ..handlers.checkin_handler import checkin_handler
from ..handlers.outlet_handler import outlet_handler
from ..handlers.summary_handler import summary_handler

logger = logging.getLogger(__name__)


# =============================================================================
# NODE FUNCTIONS (Pure functions returning partial state updates)
# =============================================================================

def classify_intent_node(state: ConversationState) -> dict:
    """
    Classify user intent from message or button action

    Args:
        state: Current conversation state

    Returns:
        Partial state update with intent classification
    """
    logger.info("🔍 CLASSIFY INTENT NODE")

    try:
        # Get user message and button action
        user_message = state.get("user_message", "")
        button_action = state.get("button_action")
        current_state = state.get("current_state", States.IDLE)

        logger.info(f"   ├── Message: '{user_message}'")
        logger.info(f"   ├── Button action: {button_action}")
        logger.info(f"   └── Current state: {current_state}")

        # If button action is present, use it directly
        if button_action:
            # Map button actions to intents
            button_upper = button_action.upper() if isinstance(button_action, str) else button_action
            if button_upper in ["CHECKIN", ButtonAction.CHECKIN]:
                intent = Intent.CHECKIN
            elif button_upper in ["AREA_VIEW", ButtonAction.AREA_VIEW]:
                intent = Intent.AREA_VIEW
            elif button_upper in ["OUTLET_DETAILS", ButtonAction.OUTLET_DETAILS]:
                intent = Intent.OUTLET_DETAILS
            elif button_upper in ["END_SUMMARY", ButtonAction.END_SUMMARY]:
                intent = Intent.END_SUMMARY
            elif button_upper in ["BACK", ButtonAction.BACK]:
                intent = Intent.GREETING  # Back goes to greeting
            else:
                intent = Intent.UNKNOWN

            logger.info(f"✅ Intent from button: {intent}")
            return {"intent": intent}

        # Otherwise, classify from message
        intent_obj = intent_classifier.classify(user_message, current_state)
        logger.info(f"✅ Classified intent: {intent_obj}")

        return {"intent": intent_obj}

    except Exception as e:
        logger.error(f"❌ Error classifying intent: {e}")
        return {"intent": Intent.UNKNOWN, "error": str(e)}


def greeting_node(state: ConversationState) -> dict:
    """
    Show greeting with 3 main buttons

    Args:
        state: Current conversation state

    Returns:
        Partial state update with greeting response
    """
    logger.info("👋 GREETING NODE")

    try:
        dsr_name = state["dsr_name"]
        logger.info(f"   └── DSR: {dsr_name}")

        # Call greeting handler
        result = greeting_handler.handle(dsr_name)

        logger.info(f"✅ Greeting generated")
        logger.info(f"   ├── Next state: {result['next_state']}")
        logger.info(f"   └── Buttons: {len(result['buttons'])} buttons")

        return {
            "response_message": result["message"],
            "response_messages": None,  # Clear multi-message field
            "response_buttons": result["buttons"],
            "template_type": result["template_type"],
            "current_state": result["next_state"],
            "previous_state": state.get("current_state")
        }

    except Exception as e:
        logger.error(f"❌ Error in greeting node: {e}")
        return {
            "error": str(e),
            "response_message": "සමාවෙන්න, දෝෂයක් සිදු විය.",
            "current_state": States.GREETING
        }


def checkin_node(state: ConversationState) -> dict:
    """
    Show daily plan check-in

    Args:
        state: Current conversation state

    Returns:
        Partial state update with check-in response
    """
    logger.info("🌅 CHECKIN NODE")

    try:
        dsr_name = state["dsr_name"]
        target_date = date.fromisoformat(state["target_date"])
        logger.info(f"   ├── DSR: {dsr_name}")
        logger.info(f"   └── Date: {target_date}")

        # Call checkin handler
        result = checkin_handler.handle(dsr_name, target_date)

        logger.info(f"✅ Check-in completed")
        logger.info(f"   ├── Next state: {result['next_state']}")
        logger.info(f"   └── Data: {result.get('data', {})}")

        return {
            "response_message": result["message"],
            "response_messages": None,  # Clear multi-message field
            "response_buttons": result["buttons"],
            "template_type": result["template_type"],
            "current_state": result["next_state"],
            "previous_state": state.get("current_state"),
            "response_data": result.get("data")
        }

    except Exception as e:
        logger.error(f"❌ Error in checkin node: {e}")
        return {
            "error": str(e),
            "response_message": "සමාවෙන්න, check-in එකේ දෝෂයක් සිදු විය.",
            "current_state": States.GREETING
        }


def area_view_node(state: ConversationState) -> dict:
    """
    Show outlets grouped by area with Google Maps links

    Args:
        state: Current conversation state

    Returns:
        Partial state update with area view response
    """
    logger.info("🗺️ AREA VIEW NODE")

    try:
        dsr_name = state["dsr_name"]
        target_date = date.fromisoformat(state["target_date"])
        logger.info(f"   ├── DSR: {dsr_name}")
        logger.info(f"   └── Date: {target_date}")

        # Call outlet handler
        result = outlet_handler.show_area_view(dsr_name, target_date)

        logger.info(f"✅ Area view generated")
        logger.info(f"   └── Next state: {result['next_state']}")

        return {
            "response_message": result["message"],
            "response_messages": None,  # Clear multi-message field
            "response_buttons": result["buttons"],
            "template_type": result["template_type"],
            "current_state": result["next_state"],
            "previous_state": state.get("current_state")
        }

    except Exception as e:
        logger.error(f"❌ Error in area view node: {e}")
        return {
            "error": str(e),
            "response_message": "සමාවෙන්න, area view එකේ දෝෂයක් සිදු විය.",
            "current_state": States.GREETING
        }


def outlet_select_node(state: ConversationState) -> dict:
    """
    Request outlet number selection

    Args:
        state: Current conversation state

    Returns:
        Partial state update with outlet selection request
    """
    logger.info("📍 OUTLET SELECT NODE")

    try:
        dsr_name = state["dsr_name"]
        target_date = date.fromisoformat(state["target_date"])
        logger.info(f"   ├── DSR: {dsr_name}")
        logger.info(f"   └── Date: {target_date}")

        # Call outlet handler
        result = outlet_handler.request_outlet_number(dsr_name, target_date)

        logger.info(f"✅ Outlet selection requested")
        logger.info(f"   └── Next state: {result['next_state']}")

        return {
            "response_message": result["message"],
            "response_messages": None,  # Clear multi-message field
            "response_buttons": result["buttons"],
            "template_type": result["template_type"],
            "current_state": result["next_state"],
            "previous_state": state.get("current_state")
        }

    except Exception as e:
        logger.error(f"❌ Error in outlet select node: {e}")
        return {
            "error": str(e),
            "response_message": "සමාවෙන්න, outlet selection එකේ දෝෂයක් සිදු විය.",
            "current_state": States.GREETING
        }


def outlet_details_node(state: ConversationState) -> dict:
    """
    Show outlet statistics and AI coaching

    Args:
        state: Current conversation state

    Returns:
        Partial state update with outlet details response
    """
    logger.info("📊 OUTLET DETAILS NODE")

    try:
        dsr_name = state["dsr_name"]
        target_date = date.fromisoformat(state["target_date"])
        outlet_number = state.get("outlet_number")

        logger.info(f"   ├── DSR: {dsr_name}")
        logger.info(f"   ├── Date: {target_date}")
        logger.info(f"   └── Outlet #: {outlet_number}")

        # Parse outlet number from message if not set
        if not outlet_number:
            user_message = state.get("user_message", "")
            try:
                outlet_number = int(user_message.strip())
            except ValueError:
                logger.warning(f"⚠️ Invalid outlet number: {user_message}")
                return {
                    "response_message": "කරුණාකර outlet number එක නිවැරදිව ඇතුළත් කරන්න (උදා: 1)",
                    "current_state": States.OUTLET_SELECT
                }

        # Call outlet handler
        result = outlet_handler.show_outlet_details(dsr_name, outlet_number, target_date)

        logger.info(f"✅ Outlet details generated")
        logger.info(f"   ├── Next state: {result['next_state']}")
        logger.info(f"   └── Data: {result.get('data', {})}")

        # Handle multiple messages (for outlet details, we send 2 separate messages)
        if "messages" in result:
            logger.info(f"   └── Sending {len(result['messages'])} separate messages")
            return {
                "response_message": "",  # Clear single message field
                "response_messages": result["messages"],  # Multiple messages to send
                "response_buttons": result["buttons"],
                "template_type": result["template_type"],
                "current_state": result["next_state"],
                "previous_state": state.get("current_state"),
                "response_data": result.get("data")
            }
        else:
            return {
                "response_message": result["message"],
                "response_messages": None,  # Clear multi-message field
                "response_buttons": result["buttons"],
                "template_type": result["template_type"],
                "current_state": result["next_state"],
                "previous_state": state.get("current_state"),
                "response_data": result.get("data")
            }

    except Exception as e:
        logger.error(f"❌ Error in outlet details node: {e}")
        return {
            "error": str(e),
            "response_message": "සමාවෙන්න, outlet details එකේ දෝෂයක් සිදු විය.",
            "current_state": States.GREETING
        }


def summary_node(state: ConversationState) -> dict:
    """
    Show end of day summary

    Args:
        state: Current conversation state

    Returns:
        Partial state update with summary response
    """
    logger.info("🌙 SUMMARY NODE")

    try:
        dsr_name = state["dsr_name"]
        target_date = date.fromisoformat(state["target_date"])
        logger.info(f"   ├── DSR: {dsr_name}")
        logger.info(f"   └── Date: {target_date}")

        # Call summary handler
        result = summary_handler.handle(dsr_name, target_date)

        logger.info(f"✅ Summary generated")
        logger.info(f"   ├── Next state: {result['next_state']}")
        logger.info(f"   └── Data: {result.get('data', {})}")

        return {
            "response_message": result["message"],
            "response_messages": None,  # Clear multi-message field
            "response_buttons": result["buttons"],
            "template_type": result["template_type"],
            "current_state": result["next_state"],
            "previous_state": state.get("current_state"),
            "response_data": result.get("data")
        }

    except Exception as e:
        logger.error(f"❌ Error in summary node: {e}")
        return {
            "error": str(e),
            "response_message": "සමාවෙන්න, summary එකේ දෝෂයක් සිදු විය.",
            "current_state": States.GREETING
        }


# =============================================================================
# ROUTING FUNCTIONS (Conditional edge logic)
# =============================================================================

def route_by_intent(state: ConversationState) -> Literal[
    "greeting",
    "checkin",
    "area_view",
    "outlet_select",
    "outlet_details",
    "summary",
    "end"
]:
    """
    Route to appropriate node based on classified intent

    Args:
        state: Current conversation state

    Returns:
        Next node name
    """
    intent = state.get("intent")
    current_state = state.get("current_state", States.IDLE)

    logger.info(f"🔀 ROUTING by intent: {intent} (state: {current_state})")

    # Route based on intent
    if intent == Intent.GREETING:
        return "greeting"
    elif intent == Intent.CHECKIN:
        return "checkin"
    elif intent == Intent.AREA_VIEW:
        return "area_view"
    elif intent == Intent.OUTLET_DETAILS:
        # Check if we need to request outlet number first
        if current_state in [States.IDLE, States.GREETING]:
            return "outlet_select"
        else:
            return "outlet_details"
    elif intent == Intent.OUTLET_NUMBER:
        # User provided outlet number - go to details
        return "outlet_details"
    elif intent == Intent.END_SUMMARY:
        return "summary"
    else:
        # Unknown intent - show greeting
        logger.warning(f"⚠️ Unknown intent: {intent} - routing to greeting")
        return "greeting"


# =============================================================================
# GRAPH CREATION
# =============================================================================

def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow

    Returns:
        Compiled StateGraph application
    """
    logger.info("🏗️ Creating LangGraph workflow...")

    # Initialize graph with state schema
    workflow = StateGraph(ConversationState)

    # Add nodes (pure functions)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("checkin", checkin_node)
    workflow.add_node("area_view", area_view_node)
    workflow.add_node("outlet_select", outlet_select_node)
    workflow.add_node("outlet_details", outlet_details_node)
    workflow.add_node("summary", summary_node)

    # Set entry point
    workflow.set_entry_point("classify_intent")

    # Add conditional edge from classify_intent to route by intent
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "greeting": "greeting",
            "checkin": "checkin",
            "area_view": "area_view",
            "outlet_select": "outlet_select",
            "outlet_details": "outlet_details",
            "summary": "summary",
            "end": END
        }
    )

    # All nodes go to END (allow fresh routing on each message)
    workflow.add_edge("greeting", END)
    workflow.add_edge("checkin", END)
    workflow.add_edge("area_view", END)
    workflow.add_edge("outlet_select", END)
    workflow.add_edge("outlet_details", END)
    workflow.add_edge("summary", END)

    # Compile with checkpointer for state persistence
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    logger.info("✅ LangGraph workflow compiled successfully")
    logger.info("   ├── Nodes: 7")
    logger.info("   ├── Entry point: classify_intent")
    logger.info("   ├── Checkpointer: MemorySaver")
    logger.info("   └── All nodes → END")

    return app


# =============================================================================
# EXPORT COMPILED WORKFLOW
# =============================================================================

# Create workflow instance at module import time
compiled_workflow = create_workflow()
