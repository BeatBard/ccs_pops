"""
LangGraph State Schema - Clean Architecture
============================================

Minimal, typed state for the DSR conversation workflow.
Following LangGraph 2026 best practices:
- Minimal state with only necessary fields
- Type annotations for all fields
- Optional fields marked accordingly
"""

from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict
from datetime import datetime


class ConversationState(TypedDict, total=False):
    """
    Minimal state for DSR conversation workflow

    Following LangGraph best practices:
    - Minimal state with only necessary fields
    - Type annotations for all fields
    - Optional fields marked accordingly
    """
    # Core identifiers
    dsr_name: str
    target_date: str  # ISO format: YYYY-MM-DD

    # State management (from States enum in constants.py)
    current_state: str
    previous_state: Optional[str]

    # User interaction
    user_message: str
    intent: Optional[str]  # From Intent enum
    button_action: Optional[str]  # From ButtonAction enum

    # Context for outlet flow
    outlet_number: Optional[int]

    # Response data
    response_message: str
    response_buttons: List[Dict[str, str]]
    template_type: str

    # Additional response data
    response_data: Optional[Dict[str, Any]]

    # Error handling
    error: Optional[str]


def create_initial_state(dsr_name: str, target_date: datetime) -> ConversationState:
    """
    Create initial state for a new conversation

    Args:
        dsr_name: Name of the DSR
        target_date: Target date for the conversation

    Returns:
        Initial conversation state
    """
    return {
        "dsr_name": dsr_name,
        "target_date": target_date.strftime("%Y-%m-%d"),
        "current_state": "IDLE",
        "previous_state": None,
        "user_message": "",
        "intent": None,
        "button_action": None,
        "outlet_number": None,
        "response_message": "",
        "response_buttons": [],
        "template_type": "text",
        "response_data": None,
        "error": None
    }
