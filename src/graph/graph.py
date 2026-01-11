"""
LangGraph Graph Compilation
Assembles the conversational flow state machine
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import ConversationState, States
from .nodes import (
    morning_checkin_node,
    outlet_arrival_node,
    visit_complete_node,
    end_of_day_node,
    error_handler_node,
)
from .menu_nodes import (
    greeting_menu_node,
    plan_view_menu_node,
    show_outlet_list_node,
    show_status_node,
    help_menu_node,
)
from .edges import route_user_input
import logging

logger = logging.getLogger(__name__)


def create_graph():
    """Create and compile the LangGraph state machine"""

    # Initialize graph with ConversationState schema
    graph = StateGraph(ConversationState)

    # Add all nodes
    # Menu navigation nodes
    graph.add_node("greeting_menu", greeting_menu_node)
    graph.add_node("plan_view_menu", plan_view_menu_node)
    graph.add_node("show_outlet_list", show_outlet_list_node)
    graph.add_node("show_status", show_status_node)
    graph.add_node("help_menu", help_menu_node)

    # Action nodes
    graph.add_node("morning_checkin", morning_checkin_node)
    graph.add_node("outlet_arrival", outlet_arrival_node)
    graph.add_node("visit_complete", visit_complete_node)
    graph.add_node("end_of_day", end_of_day_node)
    graph.add_node("error_handler", error_handler_node)

    # Set conditional entry point - routes based on user input
    graph.set_conditional_entry_point(
        route_user_input,
        {
            # Menu nodes
            "greeting_menu": "greeting_menu",
            "plan_view_menu": "plan_view_menu",
            "show_outlet_list": "show_outlet_list",
            "show_status": "show_status",
            "help_menu": "help_menu",

            # Action nodes
            "morning_checkin": "morning_checkin",
            "outlet_arrival": "outlet_arrival",
            "visit_complete": "visit_complete",
            "end_of_day": "end_of_day",
            "error": "error_handler",
        }
    )

    # All nodes END after processing - next user message triggers new routing
    # This prevents automatic chaining that reads AI messages instead of user input
    graph.add_edge("greeting_menu", END)
    graph.add_edge("plan_view_menu", END)
    graph.add_edge("show_outlet_list", END)
    graph.add_edge("show_status", END)
    graph.add_edge("help_menu", END)
    graph.add_edge("morning_checkin", END)
    graph.add_edge("outlet_arrival", END)
    graph.add_edge("visit_complete", END)
    graph.add_edge("end_of_day", END)
    graph.add_edge("error_handler", END)

    # Compile with memory checkpointer for state persistence
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)

    logger.info("LangGraph compiled successfully")
    return app


# Create the compiled graph app
graph_app = create_graph()
