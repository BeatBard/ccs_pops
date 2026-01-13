"""
WhatsApp Content Templates Configuration
=========================================

Defines static button templates for Twilio WhatsApp integration.

IMPORTANT CONSTRAINTS:
- WhatsApp allows MAX 3 Quick Reply buttons for unapproved session templates
- Button text must be under 20 characters
- Emojis are allowed in button text
- Template body uses {{1}} for dynamic content

Setup Instructions:
1. Go to Twilio Console > Messaging > Content Template Builder
2. Create Quick Reply templates with the button configurations below
3. Copy the Content SID (starts with HX...)
4. Set the environment variables in your .env file

Environment Variables:
    TWILIO_CONTENT_SID_GREETING  - Greeting menu template
    TWILIO_CONTENT_SID_AREA_VIEW - Area view template
    TWILIO_CONTENT_SID_HELP      - Help menu template
"""

import os
from typing import Dict, List, Optional
from enum import Enum


# =============================================================================
# TEMPLATE TYPES
# =============================================================================
class TemplateType(Enum):
    """
    Template types for different conversation stages.
    
    Each type corresponds to a Content Template in Twilio Console.
    """
    GREETING = "greeting"         # Main menu after greeting
    PLAN_VIEW = "plan_view"       # Plan viewing options
    OUTLET_SELECT = "outlet_select"  # Not used (outlets shown as numbered list)
    HELP = "help"                 # Help menu


# =============================================================================
# BUTTON TEMPLATE CLASS
# =============================================================================
class ButtonTemplate:
    """
    Represents a WhatsApp Quick Reply button template.
    
    Attributes:
        name: Template name for identification
        content_sid: Twilio Content Template SID (HX...)
        buttons: List of button configurations
    """

    def __init__(self, name: str, content_sid: str, buttons: List[Dict[str, str]]):
        self.name = name
        self.content_sid = content_sid
        self.buttons = buttons

    def get_button_ids(self) -> List[str]:
        """Get list of button IDs for this template."""
        return [btn["id"] for btn in self.buttons]

    def get_button_by_text(self, text: str) -> Optional[Dict[str, str]]:
        """Find button by its display text (case-insensitive)."""
        text_lower = text.lower().strip()
        for btn in self.buttons:
            if btn["text"].lower() == text_lower:
                return btn
        return None


# =============================================================================
# BUTTON TEMPLATE CONFIGURATIONS
# =============================================================================
# IMPORTANT: WhatsApp allows MAX 3 Quick Reply buttons for unapproved templates!

BUTTON_TEMPLATES = {
    # ─────────────────────────────────────────────────────────────────────────
    # GREETING MENU
    # Shown when user says Hi/Hello or after most actions
    # Maps to ButtonAction constants from src/core/constants.py
    # ─────────────────────────────────────────────────────────────────────────
    TemplateType.GREETING: ButtonTemplate(
        name="greeting_menu",
        content_sid=os.getenv("TWILIO_CONTENT_SID_GREETING", ""),
        buttons=[
            {"id": "checkin", "text": "Check-in 🌅", "action": "CHECKIN"},
            {"id": "outlet_details", "text": "Outlet විස්තර 📍", "action": "OUTLET_DETAILS"},
            {"id": "end_summary", "text": "දවස අවසානය 🌙", "action": "END_SUMMARY"}
        ]
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # AREA VIEW
    # Shown after check-in or when viewing outlets by area
    # ─────────────────────────────────────────────────────────────────────────
    TemplateType.PLAN_VIEW: ButtonTemplate(
        name="area_view",
        content_sid=os.getenv("TWILIO_CONTENT_SID_AREA_VIEW", ""),
        buttons=[
            {"id": "area_view", "text": "ප්‍රදේශ අනුව 🗺️", "action": "AREA_VIEW"},
            {"id": "outlet_details", "text": "Outlet විස්තර 📍", "action": "OUTLET_DETAILS"},
            {"id": "end_summary", "text": "දවස අවසානය 🌙", "action": "END_SUMMARY"}
        ]
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # HELP MENU
    # Shown when user needs help or types "help"
    # ─────────────────────────────────────────────────────────────────────────
    TemplateType.HELP: ButtonTemplate(
        name="help_menu",
        content_sid=os.getenv("TWILIO_CONTENT_SID_HELP", ""),
        buttons=[
            {"id": "checkin", "text": "Check-in 🌅", "action": "CHECKIN"},
            {"id": "outlet_details", "text": "Outlet විස්තර 📍", "action": "OUTLET_DETAILS"},
            {"id": "back", "text": "ආපසු 🔙", "action": "BACK"}
        ]
    )
}


# =============================================================================
# TEMPLATE ACCESS FUNCTIONS
# =============================================================================
def get_template(template_type: TemplateType) -> Optional[ButtonTemplate]:
    """
    Get button template by type.
    
    Args:
        template_type: The type of template to retrieve
        
    Returns:
        ButtonTemplate if found, None otherwise
    """
    return BUTTON_TEMPLATES.get(template_type)


def get_template_by_button_text(button_text: str) -> Optional[tuple[TemplateType, Dict[str, str]]]:
    """
    Find which template and button matches the given button text.
    
    Useful for determining user intent from button clicks.
    
    Args:
        button_text: The text of the clicked button
        
    Returns:
        Tuple of (TemplateType, button_dict) if found, None otherwise
    """
    for template_type, template in BUTTON_TEMPLATES.items():
        button = template.get_button_by_text(button_text)
        if button:
            return template_type, button
    return None


# =============================================================================
# OUTLET LIST FORMATTING
# =============================================================================
def format_outlet_list(outlets: List[Dict], show_top_n: Optional[int] = None) -> str:
    """
    Format outlet list as numbered text.
    
    Outlets are shown as a numbered list (NOT buttons) because:
    - Twilio doesn't support dynamic buttons
    - WhatsApp has a 3-button limit
    - Lists can have unlimited items
    
    User selects an outlet by typing the number.
    
    Args:
        outlets: List of outlet dictionaries with keys:
                 - outlet_id: Outlet identifier (e.g., "SD0001")
                 - outlet_name: Display name
                 - priority: "Yes" or "No"
                 - target_sales: Target sales amount
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

    # Add selection instruction
    lines.append("\n💡 *Outlet එකක් තෝරන්න:*")
    lines.append("අංකය type කරන්න (උදා: 1, 2, 3...)")

    return "\n".join(lines)


# =============================================================================
# TEMPLATE CREATION INSTRUCTIONS
# =============================================================================
TEMPLATE_INSTRUCTIONS = """
================================================================================
CREATING CONTENT TEMPLATES IN TWILIO CONSOLE
================================================================================

⚠️ IMPORTANT: WhatsApp allows MAX 3 buttons for unapproved session templates!

STEP 1: Go to Twilio Console
─────────────────────────────
Navigate to: Messaging > Content Template Builder

STEP 2: Create Quick Reply Templates (3 buttons each!)
─────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────────────┐
│ TEMPLATE 1: Greeting Menu (greeting_menu)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Type: Quick Reply                                                            │
│ Body: {{1}}  (Dynamic greeting text)                                         │
│                                                                              │
│ Buttons:                                                                     │
│   1. Check-in 🌅         (id: checkin)                                       │
│   2. Outlet විස්තර 📍    (id: outlet_details)                               │
│   3. දවස අවසානය 🌙       (id: end_summary)                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TEMPLATE 2: Area View (area_view)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Type: Quick Reply                                                            │
│ Body: {{1}}  (Dynamic message)                                               │
│                                                                              │
│ Buttons:                                                                     │
│   1. ප්‍රදේශ අනුව 🗺️      (id: area_view)                                     │
│   2. Outlet විස්තර 📍    (id: outlet_details)                               │
│   3. දවස අවසානය 🌙       (id: end_summary)                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TEMPLATE 3: Help Menu (help_menu)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Type: Quick Reply                                                            │
│ Body: {{1}}  (Dynamic message)                                               │
│                                                                              │
│ Buttons:                                                                     │
│   1. Check-in 🌅         (id: checkin)                                       │
│   2. Outlet විස්තර 📍    (id: outlet_details)                               │
│   3. ආපසු 🔙             (id: back)                                          │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 3: Copy Content SIDs
─────────────────────────
After creating each template, copy the Content SID (starts with HX...)

STEP 4: Add to .env file
────────────────────────
TWILIO_CONTENT_SID_GREETING=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_AREA_VIEW=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_HELP=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

NOTES
─────
- Quick Reply buttons work within 24-hour sessions WITHOUT approval!
- Keep button text under 20 characters
- Emojis are allowed in button text
- Error 63013 = policy violation (check message content format)

================================================================================
"""
