"""
WhatsApp Content Templates Configuration
Defines static button templates for Twilio WhatsApp

To use these templates:
1. Go to Twilio Console > Messaging > Content Template Builder
2. Create Quick Reply templates (work in 24hr session without approval)
3. Copy the Content SID (starts with HX...)
4. Set the environment variable in .env file
"""

import os
from typing import Dict, List, Optional
from enum import Enum

class TemplateType(Enum):
    """Template types for different conversation stages"""
    GREETING = "greeting"
    PLAN_VIEW = "plan_view"
    OUTLET_SELECT = "outlet_select"
    HELP = "help"


class ButtonTemplate:
    """Represents a WhatsApp button template"""

    def __init__(self, name: str, content_sid: str, buttons: List[Dict[str, str]]):
        self.name = name
        self.content_sid = content_sid
        self.buttons = buttons

    def get_button_ids(self) -> List[str]:
        """Get list of button IDs for this template"""
        return [btn["id"] for btn in self.buttons]

    def get_button_by_text(self, text: str) -> Optional[Dict[str, str]]:
        """Find button by its text (case-insensitive)"""
        text_lower = text.lower().strip()
        for btn in self.buttons:
            if btn["text"].lower() == text_lower:
                return btn
        return None


# Define button templates
# IMPORTANT: WhatsApp allows MAX 3 Quick Reply buttons for unapproved session templates!
BUTTON_TEMPLATES = {
    # Greeting menu - shown when user says Hi/Hello (3 buttons max)
    TemplateType.GREETING: ButtonTemplate(
        name="greeting_menu",
        content_sid=os.getenv("TWILIO_CONTENT_SID_GREETING", ""),
        buttons=[
            {"id": "my_plan", "text": "මගේ සැලැස්ම 📋", "action": "show_plan"},
            {"id": "my_status", "text": "තත්ත්වය 📊", "action": "show_status"},
            {"id": "checkin", "text": "Check-in ✅", "action": "morning_checkin"}
        ]
    ),

    # Plan view options - shown when user wants to see their plan (3 buttons)
    TemplateType.PLAN_VIEW: ButtonTemplate(
        name="plan_view_options",
        content_sid=os.getenv("TWILIO_CONTENT_SID_PLAN_VIEW", ""),
        buttons=[
            {"id": "top3", "text": "ප්‍රමුඛ 3 📍", "action": "show_top3"},
            {"id": "full_list", "text": "සම්පූර්ණ ලැයිස්තුව", "action": "show_full_list"},
            {"id": "back", "text": "ආපසු 🔙", "action": "back_to_greeting"}
        ]
    ),

    # Help menu (3 buttons max)
    TemplateType.HELP: ButtonTemplate(
        name="help_menu",
        content_sid=os.getenv("TWILIO_CONTENT_SID_HELP", ""),
        buttons=[
            {"id": "morning", "text": "දවස පටන් ගන්න 🌅", "action": "morning_checkin"},
            {"id": "visit", "text": "Outlet යන්න 📍", "action": "show_help_visit"},
            {"id": "record", "text": "විකුණුම් ලියන්න 💰", "action": "show_help_sales"}
        ]
    )
}


def get_template(template_type: TemplateType) -> Optional[ButtonTemplate]:
    """Get button template by type"""
    return BUTTON_TEMPLATES.get(template_type)


def get_template_by_button_text(button_text: str) -> Optional[tuple[TemplateType, Dict[str, str]]]:
    """Find which template and button matches the given button text"""
    for template_type, template in BUTTON_TEMPLATES.items():
        button = template.get_button_by_text(button_text)
        if button:
            return template_type, button
    return None


def format_outlet_list(outlets: List[Dict], show_top_n: Optional[int] = None) -> str:
    """
    Format outlet list as numbered text (NOT buttons - Twilio constraint)

    Args:
        outlets: List of outlet dictionaries
        show_top_n: If provided, show only top N outlets

    Returns:
        Formatted string with numbered outlets
    """
    if not outlets:
        return "📭 අද outlets නැහැ"

    outlets_to_show = outlets[:show_top_n] if show_top_n else outlets

    lines = ["📍 *ඔබගේ Outlets:*\n"]

    for i, outlet in enumerate(outlets_to_show, 1):
        outlet_id = outlet.get("outlet_id", "")
        outlet_name = outlet.get("outlet_name", "Unknown")
        priority = " ⭐" if outlet.get("priority") == "Yes" else ""
        target = outlet.get("target_sales", 0)

        lines.append(f"{i}. *{outlet_id}* - {outlet_name}{priority}")
        lines.append(f"   Target: LKR {target:,.0f}\n")

    # Add instruction
    lines.append("\n💡 *Outlet එකක් තෝරන්න:*")
    lines.append("අංකය type කරන්න (උදා: 1, 2, 3...)")

    return "\n".join(lines)


# Template creation instructions for Twilio Console
TEMPLATE_INSTRUCTIONS = """
# Creating Content Templates in Twilio Console

## IMPORTANT: WhatsApp allows MAX 3 buttons for unapproved session templates!

## Step 1: Go to Twilio Console
Navigate to: Messaging > Content Template Builder

## Step 2: Create Quick Reply Templates (3 buttons each!)

### Template 1: Greeting Menu (greeting_menu)
- Type: Quick Reply
- Body: {{1}}  (This allows dynamic greeting text)
- Add 3 Quick Reply Buttons:
  1. මගේ සැලැස්ම 📋 (id: my_plan)
  2. තත්ත්වය 📊 (id: my_status)
  3. Check-in ✅ (id: checkin)

### Template 2: Plan View Options (plan_view_options)
- Type: Quick Reply
- Body: {{1}}  (Dynamic message)
- Add 3 Quick Reply Buttons:
  1. ප්‍රමුඛ 3 📍 (id: top3)
  2. සම්පූර්ණ ලැයිස්තුව (id: full_list)
  3. ආපසු 🔙 (id: back)

### Template 3: Help Menu (help_menu)
- Type: Quick Reply
- Body: {{1}}  (Dynamic message)
- Add 3 Quick Reply Buttons:
  1. දවස පටන් ගන්න 🌅 (id: morning)
  2. Outlet යන්න 📍 (id: visit)
  3. විකුණුම් ලියන්න 💰 (id: record)

## Step 3: Copy Content SIDs
After creating each template, copy the Content SID (starts with HX...)

## Step 4: Add to .env file
```
TWILIO_CONTENT_SID_GREETING=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_PLAN_VIEW=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_HELP=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Note
Quick Reply buttons work within 24-hour sessions WITHOUT approval!
Keep button text under 20 characters!
"""
