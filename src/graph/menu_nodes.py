"""
Menu Navigation Nodes
Handles button-based menu navigation with Twilio Content Templates
"""

from langchain_core.messages import HumanMessage, AIMessage
from .state import ConversationState, States
from ..tools import get_daily_plan_tool, calculate_metrics_tool
from ..whatsapp import TemplateType, format_outlet_list
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def greeting_menu_node(state: ConversationState) -> ConversationState:
    """
    Show main greeting menu with 3 buttons (WhatsApp max limit):
    - මගේ සැලැස්ම 📋 (view today's plan)
    - තත්ත්වය 📊 (current progress)
    - Check-in ✅ (start the day)
    
    Note: Help is available by typing "help" - removed from buttons due to 3-button limit
    """
    logger.info("=" * 50)
    logger.info("🏠 GREETING MENU NODE")
    logger.info("=" * 50)

    try:
        dsr_name = state["dsr_name"]
        logger.info(f"👤 DSR: {dsr_name}")

        # Welcome message in Sinhala
        message = f"👋 සුභ උදෑසනක් {dsr_name}! ඔබට අද මොනවා කරන්න ඕනද?"

        logger.info("✅ Greeting menu prepared (3 buttons)")
        logger.info(f"   └── Template type: {TemplateType.GREETING.value}")

        return {
            "messages": state["messages"] + [AIMessage(content=message)],
            "current_state": States.GREETING_MENU,
            "previous_state": state.get("current_state"),
            "template_type": TemplateType.GREETING.value,
            "menu_context": "greeting_menu",
            "buttons": None,  # Template handles buttons
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in greeting_menu_node: {e}")
        return {
            "messages": state["messages"] + [AIMessage(content=f"දෝෂයක්: {str(e)}")],
            "updated_at": datetime.now().isoformat()
        }


def plan_view_menu_node(state: ConversationState) -> ConversationState:
    """
    Show plan view options with 3 buttons:
    - Top 3 Outlet
    - සම්පූර්ණ ලැයිස්තුව (Full list)
    - නැවත පසුට (Back)
    """
    logger.info("=" * 50)
    logger.info("📋 PLAN VIEW MENU NODE")
    logger.info("=" * 50)

    try:
        dsr_name = state["dsr_name"]
        today = datetime.now().strftime("%Y-%m-%d")

        # Get daily plan
        logger.info("🔧 TOOL CALL: get_daily_plan_tool")
        plan_result = get_daily_plan_tool.invoke({"dsr_name": dsr_name, "date": today})
        logger.info(f"   └── Result: {plan_result.get('total_count', 0)} outlets")

        # Store plan in state
        state["daily_plan"] = plan_result

        total = plan_result.get("total_count", 0)
        priority = plan_result.get("priority_count", 0)
        target = plan_result.get("total_target", 0)

        message = f"""📋 *අද දවසේ සැලැස්ම*

මුළු Outlets: {total}
Priority Outlets: {priority} ⭐
Target: LKR {target:,.0f}

ඔබට අදට වැදගත් Outlet බලන්න ඕනේ කොහොමද?"""

        logger.info("✅ Plan view menu prepared")
        logger.info(f"   └── Template type: {TemplateType.PLAN_VIEW.value}")

        return {
            "messages": state["messages"] + [AIMessage(content=message)],
            "current_state": States.PLAN_VIEW_MENU,
            "previous_state": state.get("current_state"),
            "daily_plan": plan_result,
            "template_type": TemplateType.PLAN_VIEW.value,
            "menu_context": "plan_view_menu",
            "buttons": None,  # Template handles buttons
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in plan_view_menu_node: {e}")
        return {
            "messages": state["messages"] + [AIMessage(content=f"දෝෂයක්: {str(e)}")],
            "updated_at": datetime.now().isoformat()
        }


def show_outlet_list_node(state: ConversationState) -> ConversationState:
    """
    Show numbered outlet list (NOT buttons - Twilio constraint)
    User selects by typing the number
    """
    logger.info("=" * 50)
    logger.info("📍 SHOW OUTLET LIST NODE")
    logger.info("=" * 50)

    try:
        # Get show_top_n from menu context (set by routing)
        show_top_n = state.get("menu_context") == "show_top3" and 3 or None

        daily_plan = state.get("daily_plan")
        if not daily_plan or not daily_plan.get("outlets"):
            message = "📭 අද ඔබට visit කරන්න outlets නැහැ"
            return {
                "messages": state["messages"] + [AIMessage(content=message)],
                "current_state": States.GREETING_MENU,
                "template_type": TemplateType.GREETING.value,
                "menu_context": "greeting_menu",
                "updated_at": datetime.now().isoformat()
            }

        outlets = daily_plan["outlets"]
        logger.info(f"   ├── Total outlets: {len(outlets)}")
        logger.info(f"   └── Showing: {'Top 3' if show_top_n == 3 else 'All'}")

        # Format outlet list with numbers
        outlet_list_text = format_outlet_list(outlets, show_top_n)

        logger.info("✅ Outlet list prepared")
        logger.info(f"   └── User will select by typing number")

        return {
            "messages": state["messages"] + [AIMessage(content=outlet_list_text)],
            "current_state": States.OUTLET_SELECT,
            "previous_state": state.get("current_state"),
            "menu_context": "outlet_select",
            "template_type": None,  # No template needed - waiting for numeric input
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in show_outlet_list_node: {e}")
        return {
            "messages": state["messages"] + [AIMessage(content=f"දෝෂයක්: {str(e)}")],
            "updated_at": datetime.now().isoformat()
        }


def show_status_node(state: ConversationState) -> ConversationState:
    """Show current day status with metrics"""
    logger.info("=" * 50)
    logger.info("📊 SHOW STATUS NODE")
    logger.info("=" * 50)

    try:
        dsr_name = state["dsr_name"]
        today = datetime.now().strftime("%Y-%m-%d")

        # Get metrics
        logger.info("🔧 TOOL CALL: calculate_metrics_tool")
        metrics = calculate_metrics_tool.invoke({"dsr_name": dsr_name, "date": today})
        logger.info(f"   └── Visited: {metrics.get('visited_count', 0)}/{metrics.get('planned_count', 0)}")

        visited = metrics.get("visited_count", 0)
        planned = metrics.get("planned_count", 0)
        route_adherence = metrics.get("route_adherence", 0)
        total_sales = metrics.get("total_sales", 0)

        message = f"""📊 *වර්තමාන තත්ත්වය*

අද visit කළ outlets: {visited} / {planned}
Route adherence: {route_adherence}%
මුළු විකුණුම: LKR {total_sales:,.0f}

{'හොඳයි! දිගටම කරන්න! 💪' if route_adherence > 70 else 'තව outlets visit කරන්න 🚗'}"""

        logger.info("✅ Status shown, returning to greeting menu")

        return {
            "messages": state["messages"] + [AIMessage(content=message)],
            "current_state": States.GREETING_MENU,
            "previous_state": state.get("current_state"),
            "template_type": TemplateType.GREETING.value,
            "menu_context": "greeting_menu",
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in show_status_node: {e}")
        return {
            "messages": state["messages"] + [AIMessage(content=f"දෝෂයක්: {str(e)}")],
            "updated_at": datetime.now().isoformat()
        }


def help_menu_node(state: ConversationState) -> ConversationState:
    """
    Show help menu with 3 buttons (WhatsApp max limit):
    - දවස පටන් ගන්න 🌅 (begin daily check-in)
    - Outlet යන්න 📍 (how to visit)
    - විකුණුම් ලියන්න 💰 (how to record)
    
    Note: Back button removed - users can type "hi" to return to main menu
    """
    logger.info("=" * 50)
    logger.info("❓ HELP MENU NODE")
    logger.info("=" * 50)

    # Help message in Sinhala
    message = "ℹ️ උදව් මෙනුව - ඔබට මොනවා ගැන උදව්වක් ඕනද? (පසුපසට යන්න 'hi' type කරන්න)"

    logger.info("✅ Help menu prepared (3 buttons)")
    logger.info(f"   └── Template type: {TemplateType.HELP.value}")

    return {
        "messages": state["messages"] + [AIMessage(content=message)],
        "current_state": States.GREETING_MENU,  # Help is part of greeting menu flow
        "previous_state": state.get("current_state"),
        "template_type": TemplateType.HELP.value,
        "menu_context": "help_menu",
        "buttons": None,
        "updated_at": datetime.now().isoformat()
    }
