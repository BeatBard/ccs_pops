"""
Operation Tools
Tools for visit tracking and metrics calculation
"""

from langchain.tools import tool
from typing import Dict, Any
from datetime import datetime
import logging
import numpy as np

logger = logging.getLogger(__name__)


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON/msgpack serialization"""
    import pandas as pd
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    return obj

# In-memory visit tracking (for POC)
# In production, this would be in a database
visit_tracker = {}


@tool
def mark_visit_tool(dsr_name: str, outlet_id: str, sales_value: float, productive: bool = True) -> Dict[str, Any]:
    """Mark an outlet as visited and record sales.

    Args:
        dsr_name: Name of the DSR
        outlet_id: Outlet identifier
        sales_value: Sales value achieved at the outlet
        productive: Whether the visit was productive (default: True)

    Returns:
        Confirmation with visit details
    """
    logger.info(f"📝 mark_visit_tool: {dsr_name} → {outlet_id} | sales={sales_value}")
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M")

        # Initialize tracker for DSR if not exists
        if dsr_name not in visit_tracker:
            visit_tracker[dsr_name] = {}

        if date not in visit_tracker[dsr_name]:
            visit_tracker[dsr_name][date] = {}

        # Record visit
        visit_tracker[dsr_name][date][outlet_id] = {
            "visit_time": time,
            "sales_value": sales_value,
            "productive": productive,
            "status": "completed"
        }
        
        logger.info(f"   └── ✅ Visit recorded at {time}")
        logger.info(f"   └── Total visits today: {len(visit_tracker[dsr_name][date])}")

        return {
            "success": True,
            "message": f"Visit to {outlet_id} recorded",
            "outlet_id": outlet_id,
            "sales_value": sales_value,
            "time": time
        }

    except Exception as e:
        logger.error(f"❌ Error in mark_visit_tool: {e}")
        return {"success": False, "error": str(e)}


@tool
def get_visit_progress_tool(dsr_name: str, date: str) -> Dict[str, Any]:
    """Get visit progress for a DSR on a specific date.

    Args:
        dsr_name: Name of the DSR
        date: Date in YYYY-MM-DD format

    Returns:
        Dictionary with visit progress details
    """
    try:
        # Get visits from tracker
        visits = visit_tracker.get(dsr_name, {}).get(date, {})

        # Calculate stats
        total_visited = len(visits)
        productive_visits = sum(1 for v in visits.values() if v.get("productive", True))
        total_sales = sum(v.get("sales_value", 0) for v in visits.values())

        visited_outlets = list(visits.keys())

        return {
            "total_visited": total_visited,
            "productive_visits": productive_visits,
            "total_sales": total_sales,
            "visited_outlets": visited_outlets,
            "visits": visits
        }

    except Exception as e:
        logger.error(f"Error in get_visit_progress_tool: {e}")
        return {"total_visited": 0, "productive_visits": 0, "total_sales": 0}


@tool
def calculate_metrics_tool(dsr_name: str, date: str) -> Dict[str, Any]:
    """Calculate performance metrics for a DSR on a specific date.

    Args:
        dsr_name: Name of the DSR
        date: Date in YYYY-MM-DD format

    Returns:
        Dictionary with performance metrics
    """
    logger.info(f"📊 calculate_metrics_tool: {dsr_name} | {date}")
    try:
        import pandas as pd
        from pathlib import Path

        DATA_DIR = Path(__file__).parent.parent.parent / "data"

        # Get planned outlets
        plan_df = pd.read_csv(DATA_DIR / "daily_plan.csv")
        plan = plan_df[(plan_df["dsr_name"] == dsr_name) & (plan_df["date"] == date)]

        planned_count = len(plan)
        planned_target = plan["target_sales"].sum() if not plan.empty else 0
        logger.info(f"   ├── Planned: {planned_count} outlets, target=LKR {planned_target:,.0f}")

        # Get actual progress
        visits = visit_tracker.get(dsr_name, {}).get(date, {})
        visited_count = len(visits)
        actual_sales = sum(v.get("sales_value", 0) for v in visits.values())
        productive_count = sum(1 for v in visits.values() if v.get("productive", True))
        logger.info(f"   ├── Visited: {visited_count} outlets, sales=LKR {actual_sales:,.0f}")
        logger.info(f"   ├── Productive: {productive_count} visits")

        # Calculate metrics
        route_adherence = (visited_count / planned_count * 100) if planned_count > 0 else 0
        target_achievement = (actual_sales / planned_target * 100) if planned_target > 0 else 0
        productive_ratio = (productive_count / visited_count * 100) if visited_count > 0 else 0

        # Outlets behind/ahead
        outlets_ahead = []
        outlets_behind = []

        if not plan.empty:
            for _, outlet_plan in plan.iterrows():
                outlet_id = outlet_plan["outlet_id"]
                target = outlet_plan["target_sales"]

                if outlet_id in visits:
                    actual = visits[outlet_id].get("sales_value", 0)
                    if actual >= target:
                        outlets_ahead.append(outlet_id)
                    else:
                        outlets_behind.append(outlet_id)

        result = {
            "planned_count": int(planned_count),
            "visited_count": int(visited_count),
            "route_adherence": float(round(route_adherence, 1)),
            "target_achievement": float(round(target_achievement, 1)),
            "productive_ratio": float(round(productive_ratio, 1)),
            "productive_visits": int(productive_count),
            "total_sales": float(actual_sales),
            "planned_target": float(planned_target),
            "outlets_ahead_count": int(len(outlets_ahead)),
            "outlets_behind_count": int(len(outlets_behind)),
            "outlets_ahead": outlets_ahead,
            "outlets_behind": outlets_behind,
        }
        
        logger.info(f"   ├── Route adherence: {route_adherence:.1f}%")
        logger.info(f"   ├── Target achievement: {target_achievement:.1f}%")
        logger.info(f"   └── Ahead: {len(outlets_ahead)}, Behind: {len(outlets_behind)}")
        
        # Convert any remaining numpy types
        return convert_numpy_types(result)

    except Exception as e:
        logger.error(f"❌ Error in calculate_metrics_tool: {e}")
        return {
            "planned_count": 0,
            "visited_count": 0,
            "route_adherence": 0,
            "target_achievement": 0
        }
