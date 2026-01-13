"""
Summary Handler
Handles end of day summary display
"""

import logging
from typing import Dict, Any
from datetime import date
from ..core.constants import States, BUTTON_LABELS, ButtonAction
from ..data.repository import repository

logger = logging.getLogger(__name__)


class SummaryHandler:
    """Handles end of day summary"""

    def handle(self, dsr_name: str, target_date: date) -> Dict[str, Any]:
        """
        Generate end of day summary

        Args:
            dsr_name: Name of the DSR
            target_date: Target date

        Returns:
            Response dictionary with summary
        """
        logger.info(f"🌙 SUMMARY HANDLER for {dsr_name} on {target_date}")

        # Get daily plan
        daily_plans = repository.get_daily_plan(dsr_name, target_date)

        if not daily_plans:
            return {
                "message": f"📭 {dsr_name}, අද ඔබට සැලසුම් කරන ලද outlets නැත.",
                "next_state": States.GREETING,
                "buttons": self._get_greeting_buttons(),
                "template_type": "greeting"
            }

        # For POC, we'll show a summary based on the plan
        # In production, this would check actual visit data

        total_planned = len(daily_plans)
        priority_planned = sum(1 for p in daily_plans if p.is_priority)
        total_target = sum(p.target_sales_litres for p in daily_plans)

        # Calculate completed (for POC, we'll say they completed some visits)
        # In real system, this would come from visit_history or tracking
        completed_visits = max(0, int(total_planned * 0.7))  # Simulating 70% completion
        priority_completed = max(0, int(priority_planned * 0.8))
        productive_visits = completed_visits  # All completed are productive

        # Calculate percentages
        route_adherence = (completed_visits / total_planned * 100) if total_planned > 0 else 0
        target_achieved = int(total_target * 0.88)  # Simulating 88% target achievement
        target_achievement_pct = (target_achieved / total_target * 100) if total_target > 0 else 0

        # Outlets performance (simulated)
        outlets_ahead = int(completed_visits * 0.6)
        outlets_behind = completed_visits - outlets_ahead
        outlets_not_visited = total_planned - completed_visits

        # Build summary message as per CLAUDE.md
        message = f"""🌙 *අද දවසේ Summary*

🎯 *ඔබේ Performance:*

📊 *සාරාංශය:*
• Visit කළ Outlets: {completed_visits} / {total_planned}
• සැලැස්ම සපුරා ගැනීම: {route_adherence:.1f}%
• Priority Outlets Covered: {priority_completed} / {priority_planned} ⭐
• සාර්ථක Visits: {productive_visits} ({(productive_visits/completed_visits*100) if completed_visits > 0 else 0:.1f}%)

💰 *විකුණුම්:*
• අද මුළු විකුණුම: {target_achieved:,.0f}L
• අද Target: {total_target:,.0f}L
• ඉලක්ක සපුරා ගැනීම: {target_achievement_pct:.1f}%

📈 *Outlets Performance:*
• Target අතිරේක: {outlets_ahead} outlets ✅
• Target අඩු: {outlets_behind} outlets ⚠️
• Visit නොකළ: {outlets_not_visited} outlets

---

💡 *හෙට දිනය සඳහා:*"""

        # Show unvisited outlets for tomorrow
        if outlets_not_visited > 0:
            unvisited_plans = daily_plans[completed_visits:][:2]  # Show first 2 unvisited
            message += f"\nඅද visit නොකළ {outlets_not_visited} outlets හෙට plan කරන්න:"
            for plan in unvisited_plans:
                message += f"\n• {plan.outlet_name} ({plan.area}) - {plan.target_sales_litres:,.0f}L Target"

        # Motivational message
        if route_adherence >= 80:
            message += f"\n\nහොඳ කොටස! අද හොඳට perform කළා! 👏"
        elif route_adherence >= 60:
            message += f"\n\nහොඳයි! හෙට තව හොඳට කරමු! 💪"
        else:
            message += f"\n\nහෙට වැඩිපුර outlets cover කරමු! ඔබට හැකියි! 🚀"

        message += "\nහෙට තව හොඳට කරමු! විශ්‍රාම ගන්න. 😊💪"

        # Buttons
        buttons = self._get_greeting_buttons()

        return {
            "message": message,
            "next_state": States.END_SUMMARY,
            "buttons": buttons,
            "template_type": "greeting",  # Use GREETING template for summary (summary not in Twilio)
            "data": {
                "completed_visits": completed_visits,
                "total_planned": total_planned,
                "route_adherence": route_adherence,
                "target_achievement": target_achievement_pct
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
summary_handler = SummaryHandler()
