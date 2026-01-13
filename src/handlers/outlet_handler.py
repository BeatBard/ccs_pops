"""
Outlet Handler
Handles outlet-related flows: area view, outlet selection, outlet details with AI coaching
"""

import logging
from typing import Dict, Any, Optional
from datetime import date
from ..core.constants import States, BUTTON_LABELS, ButtonAction
from ..data.repository import repository
from ..services.ai_service import ai_service

logger = logging.getLogger(__name__)


class OutletHandler:
    """Handles outlet viewing and details flow"""

    def show_area_view(self, dsr_name: str, target_date: date) -> Dict[str, Any]:
        """
        Show outlets grouped by area with Google Maps links

        Args:
            dsr_name: Name of the DSR
            target_date: Target date

        Returns:
            Response dictionary with area-wise outlets
        """
        logger.info(f"🗺️ AREA VIEW HANDLER for {dsr_name}")

        # Get outlets grouped by area
        area_dict = repository.get_area_wise_outlets(dsr_name, target_date)

        if not area_dict:
            return {
                "message": "📭 අද ඔබට outlets නැත.",
                "next_state": States.GREETING,
                "buttons": self._get_standard_buttons(),
                "template_type": "greeting"
            }

        # Build message with area-wise breakdown
        message_parts = ["🗺️ *ප්‍රදේශ අනුව Outlets*\n"]
        outlet_counter = 1

        for area, plans in sorted(area_dict.items()):
            message_parts.append(f"\n📍 *{area}* ({len(plans)} Outlets)")

            for plan in plans:
                # Get outlet details for Google Maps link
                outlet = repository.get_outlet_details(plan.outlet_id)

                # Priority indicator
                priority_star = "⭐ " if plan.is_priority else ""

                # Build outlet line
                message_parts.append(
                    f"{outlet_counter}. {priority_star}{plan.outlet_name} ({plan.outlet_type}) - Target: {plan.target_sales_litres:,.0f}L"
                )

                # Note: Google Maps links removed to avoid WhatsApp policy violations (Error 63013)
                # Multiple URLs in one message are flagged as spam by WhatsApp

                outlet_counter += 1

            message_parts.append("---")

        message_parts.append("\nOutlet විස්තර බලන්න outlet number එක type කරන්න (උදා: 1) 👇")

        message = "\n".join(message_parts)

        return {
            "message": message,
            "next_state": States.AREA_VIEW,
            "buttons": self._get_standard_buttons(),
            "template_type": "plan_view"  # Use PLAN_VIEW template for area view
        }

    def request_outlet_number(self, dsr_name: str, target_date: date) -> Dict[str, Any]:
        """
        Request user to input outlet number

        Args:
            dsr_name: Name of the DSR
            target_date: Target date

        Returns:
            Response dictionary requesting outlet number
        """
        logger.info(f"📍 REQUEST OUTLET NUMBER for {dsr_name}")

        # Get all outlets for today
        daily_plans = repository.get_daily_plan(dsr_name, target_date)

        if not daily_plans:
            return {
                "message": "📭 අද ඔබට outlets නැත.",
                "next_state": States.GREETING,
                "buttons": self._get_standard_buttons(),
                "template_type": "greeting"
            }

        # Build outlet list
        message_parts = ["📍 *Outlet විස්තර*\n"]
        message_parts.append("කරුණාකර ඔබට විස්තර බලන්න ඕන outlet එකේ number එක type කරන්න:\n")
        message_parts.append("උදාහරණය: 1 (Saman's Mart සඳහා)\n")
        message_parts.append("ඔබේ අද දවසේ outlets:")

        for idx, plan in enumerate(daily_plans, 1):
            priority_star = "⭐ " if plan.is_priority else ""
            message_parts.append(f"{idx}. {priority_star}{plan.outlet_name} ({plan.area})")

        message = "\n".join(message_parts)

        return {
            "message": message,
            "next_state": States.OUTLET_SELECT,
            "buttons": self._get_standard_buttons(),
            "template_type": "plan_view"  # Use PLAN_VIEW template (outlet_select not in Twilio)
        }

    def show_outlet_details(
        self,
        dsr_name: str,
        outlet_number: int,
        target_date: date
    ) -> Dict[str, Any]:
        """
        Show detailed outlet statistics and AI coaching

        Args:
            dsr_name: Name of the DSR
            outlet_number: Outlet number from list (1-indexed)
            target_date: Target date

        Returns:
            Response dictionary with outlet details and AI coaching
        """
        logger.info(f"📊 OUTLET DETAILS for outlet #{outlet_number}")

        # Get daily plan to map number to outlet_id
        daily_plans = repository.get_daily_plan(dsr_name, target_date)

        if not daily_plans or outlet_number < 1 or outlet_number > len(daily_plans):
            return {
                "message": f"❌ වලංගු නොවන outlet number: {outlet_number}\n\nකරුණාකර 1 සිට {len(daily_plans)} අතර අංකයක් ඇතුළත් කරන්න.",
                "next_state": States.OUTLET_SELECT,
                "buttons": self._get_standard_buttons(),
                "template_type": "plan_view"  # Use PLAN_VIEW template (outlet_select not in Twilio)
            }

        # Get the selected outlet (1-indexed)
        selected_plan = daily_plans[outlet_number - 1]
        outlet_id = selected_plan.outlet_id

        # Get complete outlet statistics
        stats = repository.get_outlet_statistics(dsr_name, outlet_id, target_date)

        if not stats:
            return {
                "message": f"❌ Outlet එකේ විස්තර සොයා ගත නොහැකි විය: {outlet_id}",
                "next_state": States.GREETING,
                "buttons": self._get_standard_buttons(),
                "template_type": "greeting"
            }

        # Build statistics message (Message 1 as per CLAUDE.md)
        stats_message = self._build_statistics_message(stats)

        # Generate AI coaching (Message 2 as per CLAUDE.md)
        coaching_message = self._generate_coaching(dsr_name, stats)

        # Return TWO separate messages to avoid WhatsApp policy violations (Error 63013)
        # Long messages with complex Sinhala content trigger spam detection
        return {
            "messages": [stats_message, coaching_message],  # Send as 2 separate messages
            "next_state": States.OUTLET_DETAILS,
            "buttons": self._get_standard_buttons(),
            "template_type": "plan_view",  # Use PLAN_VIEW template (outlet_details not in Twilio)
            "data": {
                "outlet_id": outlet_id,
                "outlet_name": stats.outlet.outlet_name
            }
        }

    def _build_statistics_message(self, stats) -> str:
        """Build outlet statistics message"""
        outlet = stats.outlet
        plan = stats.daily_plan
        monthly = stats.monthly_target

        # Check if ahead or behind target
        target_status = "✅ (Target අතිරේකයි)" if stats.last_visit_sales >= plan.target_sales_litres else "⚠️ (Target අඩුයි)"

        # Build message
        message = f"""📊 *{outlet.outlet_name} - {outlet.outlet_type} Outlet*

🏪 *Outlet විස්තර:*
• වර්ගය: {outlet.outlet_type}
• ප්‍රදේශය: {outlet.area}
• Priority: {'⭐ ඉහළ' if plan.is_priority else '⬜ සාමාන්‍ය'}

📈 *විකුණුම් දත්ත:*
• අද Target: {plan.target_sales_litres:,.0f}L
• පසුගිය visit: {stats.last_visit_sales:,.0f}L {target_status}
• අවසන් මාස 3 සාමාන්‍යය: {stats.last_3_months_avg:,.0f}L/visit
• මාසික Target: {monthly.monthly_target_litres:,.0f}L
• මාසික සම්පූර්ණ කළ ප්‍රමාණය: {monthly.monthly_completed_litres:,.0f}L ({monthly.completion_percentage:.1f}%)

🔝 *වඩාත්ම විකුණෙන භාණ්ඩ:*"""

        # Add top SKUs
        for idx, sku in enumerate(stats.top_skus[:3], 1):
            message += f"\n{idx}. {sku.sku_name} - {sku.avg_sales_per_visit_litres:,.0f}L/visit"

        # Add special notes
        message += f"\n\n💡 *විශේෂ සටහන:*"
        message += f"\n• Cooler ඇත: {'✅ Yes' if outlet.cooler_available == 'Yes' else '❌ No'}"
        message += f"\n• Shelf space: {outlet.shelf_space_sqft} sqft"

        if outlet.poi_list:
            message += f"\n• ප්‍රදේශය: {', '.join(outlet.poi_list)} අසල"

        return message

    def _generate_coaching(self, dsr_name: str, stats) -> str:
        """Generate AI coaching message"""
        logger.info("🤖 Generating AI coaching...")

        try:
            # Prepare context for AI
            context = {
                "dsr_name": dsr_name,
                "outlet_name": stats.outlet.outlet_name,
                "outlet_type": stats.outlet.outlet_type,
                "area": stats.outlet.area,
                "target": stats.daily_plan.target_sales_litres,
                "last_visit": stats.last_visit_sales,
                "three_month_avg": stats.last_3_months_avg,
                "top_skus": [
                    {"name": sku.sku_name, "sales": sku.avg_sales_per_visit_litres}
                    for sku in stats.top_skus[:3]
                ],
                "poi_nearby": stats.outlet.poi_list,
                "monthly_completion": stats.monthly_target.completion_percentage
            }

            coaching = ai_service.generate_outlet_coaching(context)
            return f"💡 *Coaching Tips - Gemini AI*\n\n{coaching}"

        except Exception as e:
            logger.error(f"AI coaching generation failed: {e}")
            # Fallback message
            return """💡 *Coaching Tips*

• පසුගිය visit එකේ performance බලලා අද වැඩිපුර විකුණන්න try කරන්න
• Top විකුණෙන භාණ්ඩ promote කරන්න
• Customer handling skills use කරලා හොඳ relationship එකක් build කරන්න

ඔබට හැකියි! 💪"""

    def _get_standard_buttons(self):
        """Get standard navigation buttons"""
        return [
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


# Global instance
outlet_handler = OutletHandler()
