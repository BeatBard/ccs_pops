"""
Data Access Tools
Tools for querying CSV data
"""

from langchain.tools import tool
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON/msgpack serialization"""
    import numpy as np
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


@tool
def get_daily_plan_tool(dsr_name: str, date: str) -> Dict[str, Any]:
    """Get the daily outlet visit plan for a DSR.

    Args:
        dsr_name: Name of the DSR (e.g., "Nalin Perera")
        date: Date in YYYY-MM-DD format (e.g., "2026-01-11")

    Returns:
        Dictionary with outlet plan details including total count, priority outlets, and breakdown
    """
    logger.debug(f"📊 get_daily_plan_tool called: dsr={dsr_name}, date={date}")
    try:
        plan_df = pd.read_csv(DATA_DIR / "daily_plan.csv")
        logger.debug(f"   └── Loaded {len(plan_df)} rows from daily_plan.csv")
        plan = plan_df[
            (plan_df["dsr_name"] == dsr_name) & (plan_df["date"] == date)
        ]
        logger.debug(f"   └── Filtered to {len(plan)} rows for {dsr_name} on {date}")

        if plan.empty:
            logger.warning(f"   └── No plan found!")
            return {
                "outlets": [],
                "total_count": 0,
                "priority_count": 0,
                "message": f"No plan found for {dsr_name} on {date}"
            }

        outlets = plan.to_dict("records")
        priority_count = len(plan[plan["priority"] == "Yes"])

        # Calculate breakdown by type
        breakdown = {}
        for outlet in outlets:
            outlet_type = outlet.get("outlet_type", "Unknown")
            breakdown[outlet_type] = breakdown.get(outlet_type, 0) + 1

        result = {
            "outlets": outlets,
            "total_count": int(len(outlets)),
            "priority_count": int(priority_count),
            "breakdown": breakdown,
            "total_target": float(plan["target_sales"].sum()) if "target_sales" in plan.columns else 0.0
        }
        
        # Convert all numpy types to native Python types
        return convert_numpy_types(result)

    except Exception as e:
        logger.error(f"Error in get_daily_plan_tool: {e}")
        return {"error": str(e), "outlets": [], "total_count": 0}


@tool
def get_outlet_info_tool(outlet_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific outlet.

    Args:
        outlet_id: Outlet identifier (e.g., "SD0001")

    Returns:
        Dictionary with outlet details including name, type, POIs, traffic level, etc.
    """
    try:
        outlet_df = pd.read_csv(DATA_DIR / "outlet_details.csv")
        outlet = outlet_df[outlet_df["outlet_id"] == outlet_id]

        if outlet.empty:
            return {"error": f"Outlet {outlet_id} not found"}

        outlet_data = outlet.iloc[0].to_dict()

        # Parse POI data
        poi_str = outlet_data.get("poi_nearby", "")
        outlet_data["pois"] = poi_str.split("|") if poi_str else []

        # Convert numpy types to native Python types
        return convert_numpy_types(outlet_data)

    except Exception as e:
        logger.error(f"Error in get_outlet_info_tool: {e}")
        return {"error": str(e)}


@tool
def get_lipb_tracking_tool(dsr_name: str, outlet_id: str) -> Dict[str, Any]:
    """Get LIPB (Lines in Primary Billing) tracking data for a DSR at a specific outlet.

    Args:
        dsr_name: Name of the DSR
        outlet_id: Outlet identifier

    Returns:
        Dictionary with LIPB metrics including average, target, trend
    """
    try:
        lipb_df = pd.read_csv(DATA_DIR / "lipb_tracking.csv")
        lipb = lipb_df[
            (lipb_df["dsr_name"] == dsr_name) & (lipb_df["outlet_id"] == outlet_id)
        ]

        if lipb.empty:
            return {
                "error": f"No LIPB data for {dsr_name} at {outlet_id}",
                "avg_lipb": 0,
                "target_lipb": 3
            }

        lipb_data = lipb.iloc[0].to_dict()

        # Add analysis
        avg = lipb_data.get("avg_lipb", 0)
        target = lipb_data.get("target_lipb", 3)
        gap = target - avg

        lipb_data["gap"] = float(gap)
        lipb_data["needs_improvement"] = bool(gap > 0.5)

        # Convert numpy types to native Python types
        return convert_numpy_types(lipb_data)

    except Exception as e:
        logger.error(f"Error in get_lipb_tracking_tool: {e}")
        return {"error": str(e), "avg_lipb": 0}


@tool
def get_top_skus_tool(outlet_id: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """Get top selling SKUs for a specific outlet.

    Args:
        outlet_id: Outlet identifier
        top_n: Number of top SKUs to return (default: 5)

    Returns:
        List of top SKUs with sales data and stock status
    """
    try:
        sku_df = pd.read_csv(DATA_DIR / "sku_performance_by_outlet.csv")
        skus = sku_df[sku_df["outlet_id"] == outlet_id]

        if skus.empty:
            return []

        # Sort by rank and get top N
        skus = skus.sort_values("rank").head(top_n)

        sku_list = []
        for _, sku in skus.iterrows():
            sku_list.append({
                "sku_name": str(sku["sku_name"]),
                "sales_last_week": int(sku["sales_last_week"]) if pd.notna(sku["sales_last_week"]) else 0,
                "stock_status": str(sku["stock_status"]) if pd.notna(sku["stock_status"]) else "",
                "rank": int(sku["rank"]) if pd.notna(sku["rank"]) else 0
            })

        return sku_list

    except Exception as e:
        logger.error(f"Error in get_top_skus_tool: {e}")
        return []


@tool
def get_coaching_tips_tool(category: str, situation: str = "", dsr_strength: str = "") -> List[str]:
    """Get rule-based coaching tips based on category and situation.

    Args:
        category: Tip category (e.g., "Upselling", "Shelf Visibility")
        situation: Specific situation (e.g., "Low LIPB")
        dsr_strength: DSR's strength area

    Returns:
        List of coaching tips in Sinhala
    """
    try:
        tips_df = pd.read_csv(DATA_DIR / "coaching_tips.csv")

        # Filter by category
        filtered = tips_df[tips_df["category"] == category]

        # Further filter by situation if provided
        if situation:
            filtered = filtered[filtered["situation"].str.contains(situation, case=False, na=False)]

        # Prefer tips matching DSR strength
        if dsr_strength and not filtered.empty:
            strength_match = filtered[filtered["strength_area"] == dsr_strength]
            if not strength_match.empty:
                filtered = strength_match

        if filtered.empty:
            return ["මේ අවස්ථාව සඳහා ඔබට හොඳම කෙරෙන්නේ ඔබගේ අත්දැකීම් භාවිතා කිරීමයි!"]

        # Return Sinhala tips - ensure they are strings
        tips = [str(tip) for tip in filtered["tip_sinhala"].tolist()[:3]]  # Max 3 tips
        return tips

    except Exception as e:
        logger.error(f"Error in get_coaching_tips_tool: {e}")
        return []
