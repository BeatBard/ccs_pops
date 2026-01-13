"""
Greeting Handler
Handles initial greeting and welcome message
"""

import logging
from typing import Dict, Any
from ..core.constants import States, BUTTON_LABELS, ButtonAction

logger = logging.getLogger(__name__)


class GreetingHandler:
    """Handles greeting flow"""

    def handle(self, dsr_name: str) -> Dict[str, Any]:
        """
        Handle initial greeting

        Args:
            dsr_name: Name of the DSR

        Returns:
            Response dictionary with message and buttons
        """
        logger.info(f"👋 GREETING HANDLER for {dsr_name}")

        # Welcome message in Sinhala as per CLAUDE.md
        message = (
            f"👋 සුභ උදෑසනක් {dsr_name}!\n"
            f"මම ඔබේ Pocket Coach 🎯\n"
            f"ඔබේ දවසේ සෑම අවස්ථාවකම ඔබට උදව් කරන්න මම සූදානම්!\n"
            f"මම ඔබට කරන්න පුළුවන්:\n"
            f"• දවස Check-in කරන්න සහ plan එක බලන්න\n"
            f"• Outlet විස්තර සහ coaching ලබා ගන්න\n"
            f"• දවසේ summary එක බලන්න\n"
            f"ඔබට අද මොනවා කරන්න ඕනද? 💪"
        )

        # Button configuration
        buttons = [
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

        return {
            "message": message,
            "next_state": States.GREETING,
            "buttons": buttons,
            "template_type": "greeting"
        }


# Global instance
greeting_handler = GreetingHandler()
