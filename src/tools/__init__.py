"""
LangChain Tools for CCS POPS
All data access and operation tools
"""

from .data_tools import (
    get_daily_plan_tool,
    get_outlet_info_tool,
    get_lipb_tracking_tool,
    get_top_skus_tool,
    get_coaching_tips_tool,
)
from .operation_tools import (
    mark_visit_tool,
    calculate_metrics_tool,
    get_visit_progress_tool,
)
from .ai_tools import generate_ai_coaching_tool

# All tools for the agent
ALL_TOOLS = [
    get_daily_plan_tool,
    get_outlet_info_tool,
    get_lipb_tracking_tool,
    get_top_skus_tool,
    get_coaching_tips_tool,
    mark_visit_tool,
    calculate_metrics_tool,
    get_visit_progress_tool,
    generate_ai_coaching_tool,
]

__all__ = [
    "get_daily_plan_tool",
    "get_outlet_info_tool",
    "get_lipb_tracking_tool",
    "get_top_skus_tool",
    "get_coaching_tips_tool",
    "mark_visit_tool",
    "calculate_metrics_tool",
    "get_visit_progress_tool",
    "generate_ai_coaching_tool",
    "ALL_TOOLS",
]
