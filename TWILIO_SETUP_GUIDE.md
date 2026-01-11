# Twilio WhatsApp Button Setup Guide

## Overview

This guide explains how to set up WhatsApp interactive buttons using Twilio Content Templates for the DSR Sales Coaching Assistant.

---

## Why Content Templates?

Twilio WhatsApp requires **Content Templates** for interactive buttons. These are:
- Pre-defined message templates with buttons
- Work within 24-hour sessions WITHOUT approval (for Quick Reply buttons)
- Created once in Twilio Console, then reused via Content SID

**Important**: You cannot send buttons dynamically. All button text must be pre-defined in templates.

---

## Required Templates

You need to create **3 Content Templates** in Twilio Console:

### 1. Greeting Menu Template
**Name**: `greeting_menu`
**Type**: Quick Reply
**Body**: `{{1}}`

**Buttons** (4):

| # | Button Text (visible to user) | Button ID (internal, not visible) |
|---|------------------------------|----------------------------------|
| 1 | මගේ අද දවසේ සැලැස්ම | `my_plan` |
| 2 | මගේ වර්තමාන තත්ත්වය | `my_status` |
| 3 | උදව් අවශ්‍යයි | `help` |
| 4 | අද Check-in කරන්න | `checkin` |

### 2. Plan View Template
**Name**: `plan_view_options`
**Type**: Quick Reply
**Body**: `{{1}}`

**Buttons** (3):

| # | Button Text (visible to user) | Button ID (internal, not visible) |
|---|------------------------------|----------------------------------|
| 1 | Top 3 Outlet | `top3` |
| 2 | සම්පූර්ණ ලැයිස්තුව | `full_list` |
| 3 | නැවත පසුට | `back` |

### 3. Help Menu Template
**Name**: `help_menu`
**Type**: Quick Reply
**Body**: `{{1}}`

**Buttons** (4):

| # | Button Text (visible to user) | Button ID (internal, not visible) |
|---|------------------------------|----------------------------------|
| 1 | දවස පටන් ගන්න 🌅 | `morning` |
| 2 | Outlet Visit 📍 | `visit` |
| 3 | විකුණුම් Record 💰 | `record` |
| 4 | නැවත පසුට | `back` |

---

## Step-by-Step Setup

### Step 1: Access Twilio Console
1. Go to https://console.twilio.com
2. Navigate to **Messaging** → **Content Template Builder**

### Step 2: Create Template
Click **Create new template**

### Step 3: Template Configuration

#### Basic Information:
- **Template Name**: `greeting_menu` (for first template)
- **Template Language**: Sinhala (`si`)
- **Category**: `UTILITY`
- **Use Case**: Customer service/support

#### Template Type:
- Select **Quick Reply**

#### Body Content:
- Add variable: `{{1}}`

  This allows us to send dynamic greeting text while keeping buttons static.

#### Add Buttons:
Click **Add Quick Reply Button** and fill in both fields for each button:

**Example for Greeting Menu**:

| Button | Button Text Field | ID Field |
|--------|------------------|----------|
| Button 1 | මගේ අද දවසේ සැලැස්ම | `my_plan` |
| Button 2 | මගේ වර්තමාන තත්ත්වය | `my_status` |
| Button 3 | උදව් අවශ්‍යයි | `help` |
| Button 4 | අද Check-in කරන්න | `checkin` |

**Important Notes**:
- **Button Text**: This is what the user sees and clicks
- **ID**: Internal identifier (not visible to user) - use simple lowercase IDs
- Both fields are required

### Step 4: Submit (Don't Need Approval)
- Quick Reply buttons work in 24-hour sessions **without** WhatsApp approval
- Click **Submit** (no need to wait for approval)

### Step 5: Copy Content SID
After submission:
1. Click on your template
2. Copy the **Content SID** (starts with `HX...`)
3. Add to `.env` file

### Step 6: Repeat for All 3 Templates
Create all three templates following the same steps.

---

## Configuration in .env

After creating all templates, add their Content SIDs to your `.env` file:

```bash
# Twilio WhatsApp Content Template SIDs
TWILIO_CONTENT_SID_GREETING=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_PLAN_VIEW=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_HELP=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Button Text Mapping

The system maps button text to actions. **Button text must match exactly** (case-insensitive):

### Greeting Menu:
| Button Text | Action |
|------------|--------|
| මගේ අද දවසේ සැලැස්ම | Show plan view menu |
| මගේ වර්තමාන තත්ත්වය | Show current status |
| උදව් අවශ්‍යයි | Show help menu |
| අද Check-in කරන්න | Start morning check-in |

### Plan View Menu:
| Button Text | Action |
|------------|--------|
| Top 3 Outlet | Show top 3 outlets as numbered list |
| සම්පූර්ණ ලැයිස්තුව | Show all outlets as numbered list |
| නැවත පසුට | Back to greeting menu |

### Help Menu:
| Button Text | Action |
|------------|--------|
| දවස පටන් ගන්න 🌅 | Start morning check-in |
| Outlet Visit 📍 | Show help about visiting |
| විකුණුම් Record 💰 | Show help about sales |
| නැවත පසුට | Back to greeting menu |

---

## Testing Without Templates

If you haven't set up Content Templates yet, the system will:
1. Attempt to use templates (if Content SIDs are in `.env`)
2. Fallback to **plain text** messages if templates fail
3. Still work correctly, but without clickable buttons

Users can still type the button text manually.

---

## Workflow Flow

### 1. User sends "Hi" or "Hello"
→ System shows **Greeting Menu** (with 4 buttons)

### 2. User clicks "මගේ අද දවසේ සැලැස්ම"
→ System shows **Plan View Menu** (with 3 buttons)

### 3. User clicks "Top 3 Outlet"
→ System shows numbered list:
```
📍 ඔබගේ Outlets:

1. SD0001 - Spar Supermarket - Colombo 07 ⭐
   Target: LKR 18,000

2. SD0002 - Green Cabin Restaurant
   Target: LKR 16,000

3. SD0003 - Food City - Wellawatte
   Target: LKR 16,000

💡 Outlet එකක් තෝරන්න:
අංකය type කරන්න (උදා: 1, 2, 3...)
```

### 4. User types "1"
→ System routes to outlet SD0001 and provides coaching

---

## Important Constraints

### ❌ Cannot Do:
- **Dynamic button text** (e.g., outlet names as buttons)
- **More than 3-4 buttons per template** (WhatsApp limit)
- **Change button text based on data** (must be static)

### ✅ Can Do:
- **Dynamic message body** using `{{1}}` variable
- **Numbered lists** for selections
- **Button navigation** between menus
- **Mixed interactions** (buttons + text input)

---

## Troubleshooting

### Content Template Not Working?
1. **Check Content SID** in `.env` - must start with `HX`
2. **Verify template language** matches user language
3. **Check button text** matches exactly (including emojis)
4. **Ensure 24-hour session** - first message from user must be within 24 hours

### Buttons Not Clickable?
- **Missing Content SID** → System falls back to plain text
- **Template not submitted** → Submit in Twilio Console
- **Wrong template language** → Must match conversation language

### User Response Not Recognized?
- **Check button text mapping** in `src/graph/edges.py` → `BUTTON_TEXT_MAP`
- **Case sensitivity** → System handles case-insensitive matching
- **Extra spaces** → System trims whitespace

---

## Code Structure

### Files Involved:

1. **src/whatsapp/templates.py**
   - Defines all button templates
   - Maps buttons to actions
   - Contains setup instructions

2. **src/graph/edges.py**
   - Routes button clicks to appropriate nodes
   - Maps button text to actions

3. **src/graph/menu_nodes.py**
   - Handles menu display
   - Formats outlet lists
   - Manages menu navigation

4. **main.py**
   - Sends messages with Content Templates
   - Falls back to plain text if needed

---

## Development Tips

### Adding New Buttons:
1. Create new Content Template in Twilio Console
2. Add to `src/whatsapp/templates.py` → `BUTTON_TEMPLATES`
3. Add button text mapping in `src/graph/edges.py` → `BUTTON_TEXT_MAP`
4. Create corresponding node in `menu_nodes.py` if needed
5. Update routing in `route_user_input()` function

### Testing Locally:
- Use plain text fallback for initial testing
- Create templates once workflow is stable
- Test with real WhatsApp number for button functionality

---

## Resources

- [Twilio WhatsApp Buttons Documentation](https://www.twilio.com/docs/whatsapp/buttons)
- [Content Template Builder](https://console.twilio.com/us1/develop/sms/content-template-builder)
- [WhatsApp Business Policy](https://www.whatsapp.com/legal/business-policy)

---

**Last Updated**: 2026-01-11
**Status**: ✅ Implementation Complete
