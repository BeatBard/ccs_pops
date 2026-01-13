"""
Check-in Handler
Handles check-in flow and daily plan display
"""

import logging
from typing import Dict, Any
from datetime import date
from collections import Counter
from ..core.constants import States, BUTTON_LABELS, ButtonAction
from ..data.repository import repository

logger = logging.getLogger(__name__)


class CheckinHandler:
    """Handles check-in and daily plan flow"""

    def handle(self, dsr_name: str, target_date: date) -> Dict[str, Any]:
        """
        Handle check-in request

        Args:
            dsr_name: Name of the DSR
            target_date: Target date for plan

        Returns:
            Response dictionary with plan summary
        """
        logger.info(f"🌅 CHECKIN HANDLER for {dsr_name} on {target_date}")

        # Get daily plan
        daily_plans = repository.get_daily_plan(dsr_name, target_date)

        if not daily_plans:
            return {
                "message": f"📭 {dsr_name}, අද ඔබට සැලසුම් කරන ලද outlets නැත.",
                "next_state": States.GREETING,
                "buttons": self._get_greeting_buttons(),
                "template_type": "greeting"
            }

        # Calculate statistics
        total_outlets = len(daily_plans)
        priority_outlets = sum(1 for p in daily_plans if p.is_priority)

        # Count by outlet type
        type_counts = Counter(p.outlet_type for p in daily_plans)
        type_breakdown = ", ".join([f"{t} ({c})" for t, c in type_counts.items()])

        # Get unique areas
        areas = sorted(set(p.area for p in daily_plans))
        areas_text = ", ".join(areas[:5])  # Show first 5 areas
        if len(areas) > 5:
            areas_text += f" සහ තවත් {len(areas) - 5}"

        # Calculate total target
        total_target = sum(p.target_sales_litres for p in daily_plans)

        # Build message as per CLAUDE.md
        message = f"""🌅 *අද දවසේ සැලැස්ම*

📊 අද ඔබේ Plan එක:
• මුළු Outlets: {total_outlets}
• Priority Outlets: {priority_outlets} ⭐
• Outlet වර්ග: {type_breakdown}
• ප්‍රදේශ: {areas_text}

🎯 අද දවසේ Target: {total_target:,.0f}L

හොඳ දවසක් ගත කරන්න! ඔබ කැමති මොනවාද බලන්න? 🚀"""

        # Buttons for next actions
        buttons = [
            {
                "id": ButtonAction.AREA_VIEW,
                "text": BUTTON_LABELS[ButtonAction.AREA_VIEW],
                "action": ButtonAction.AREA_VIEW
            },
            {
                "id": ButtonAction.OUTLET_DETAILS,
                "text": BUTTON_LABELS[ButtonAction.OUTLET_DETAILS],
                "action": ButtonAction.OUTLET_DETAILS
            },
            {
                "id": ButtonAction.END_SUMMARY,
                "text": BUTTON_LABELS[ButtonAction.END_SUMMARY],
                "action": ButtonAction.END_SUMMARY
            }
        ]

        return {
            "message": message,
            "next_state": States.CHECKIN,
            "buttons": buttons,
            "template_type": "plan_view",  # Use PLAN_VIEW template after check-in
            "data": {
                "total_outlets": total_outlets,
                "priority_outlets": priority_outlets,
                "total_target": total_target
            }
        }

    def _get_greeting_buttons(self):
        """Get standard greeting buttons"""
        return [
            {
                "id": ButtonAction.CHECKIN,
                "text": BUTTON_LABELS[ButtonAction.CHECKIN],
                "action": ButtonAction.CHECKIN
            },
            {
                "id": ButtonAction.OUTLET_DETAILS,
                "text": BUTTON_LABELS[ButtonAction.OUTLET_DETAILS],
                "action": ButtonAction.OUTLET_DETAILS
            },
            {
                "id": ButtonAction.END_SUMMARY,
                "text": BUTTON_LABELS[ButtonAction.END_SUMMARY],
                "action": ButtonAction.END_SUMMARY
            }
        ]


# Global instance
checkin_handler = CheckinHandler()
