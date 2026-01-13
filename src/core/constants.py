"""
Core Constants and Enums
All constants used across the application
"""

from enum import Enum


class States(str, Enum):
    """Conversation states"""
    IDLE = "IDLE"
    GREETING = "GREETING"
    CHECKIN = "CHECKIN"
    AREA_VIEW = "AREA_VIEW"
    OUTLET_SELECT = "OUTLET_SELECT"
    OUTLET_DETAILS = "OUTLET_DETAILS"
    END_SUMMARY = "END_SUMMARY"


class Intent(str, Enum):
    """User intents"""
    GREETING = "greeting"
    CHECKIN = "checkin"
    OUTLET_DETAILS = "outlet_details"
    AREA_VIEW = "area_view"
    END_SUMMARY = "end_summary"
    OUTLET_NUMBER = "outlet_number"
    UNKNOWN = "unknown"


class ButtonAction(str, Enum):
    """Button actions"""
    CHECKIN = "checkin"
    OUTLET_DETAILS = "outlet_details"
    END_SUMMARY = "end_summary"
    AREA_VIEW = "area_view"
    BACK = "back"


# Button labels in Sinhala
BUTTON_LABELS = {
    ButtonAction.CHECKIN: "✅ Check-in 🌅",
    ButtonAction.OUTLET_DETAILS: "📍 Outlet විස්තර",
    ButtonAction.END_SUMMARY: "🌙 දවස අවසානය",
    ButtonAction.AREA_VIEW: "🗺️ ප්‍රදේශ අනුව Outlets",
    ButtonAction.BACK: "🔙 ආපසු",
}


# Greeting keywords
GREETING_KEYWORDS = [
    "hi", "hello", "hey", "හායි", "හෙලෝ", "හෙල්ලෝ",
    "සුබ උදෑසනක්", "සුභ උදෑසනක්", "good morning"
]


# Date format
DATE_FORMAT = "%Y-%m-%d"
