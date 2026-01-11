"""
LangGraph State Schema
Defines the conversation state structure
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from datetime import datetime


class ConversationState(TypedDict):
    """
    State schema for the sales coaching conversation
    """
    # Messages history
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # User context
    dsr_name: str
    dsr_phone: str
    dsr_profile: Optional[dict]

    # Conversation state
    current_state: str  # IDLE, GREETING, ACTIVE, AT_OUTLET, COACHING, DAY_COMPLETE
    previous_state: Optional[str]

    # Session context
    current_outlet: Optional[str]
    outlets_visited_today: list[str]
    daily_plan: Optional[dict]

    # Flags
    morning_checkin_done: bool
    end_of_day_done: bool

    # Interactive elements
    buttons: Optional[list[dict]]  # Button configurations for WhatsApp interactive messages
    template_type: Optional[str]  # Current template type being shown (greeting, plan_view, etc.)
    menu_context: Optional[str]  # Current menu context (greeting_menu, plan_view, outlet_select, etc.)

    # Metadata
    conversation_id: str
    created_at: str
    updated_at: str


# State constants
class States:
    """Conversation state constants"""
    IDLE = "IDLE"
    GREETING_MENU = "GREETING_MENU"  # Showing main greeting menu
    PLAN_VIEW_MENU = "PLAN_VIEW_MENU"  # Showing plan view options
    OUTLET_SELECT = "OUTLET_SELECT"  # User selecting outlet from numbered list
    AWAITING_RESPONSE = "AWAITING_RESPONSE"
    ACTIVE = "ACTIVE"
    AT_OUTLET = "AT_OUTLET"
    COACHING = "COACHING"
    VISIT_TRACKING = "VISIT_TRACKING"
    DAY_COMPLETE = "DAY_COMPLETE"


def create_initial_state(phone_number: str, dsr_name: str = "Nalin Perera") -> ConversationState:
    """Create initial conversation state"""
    now = datetime.now().isoformat()

    return ConversationState(
        messages=[],
        dsr_name=dsr_name,
        dsr_phone=phone_number,
        dsr_profile=None,
        current_state=States.IDLE,
        previous_state=None,
        current_outlet=None,
        outlets_visited_today=[],
        daily_plan=None,
        morning_checkin_done=False,
        end_of_day_done=False,
        buttons=None,
        template_type=None,
        menu_context=None,
        conversation_id=f"{phone_number}_{now}",
        created_at=now,
        updated_at=now
    )
