# Workflow Changes Summary - Button-Based Navigation

## Overview

The WhatsApp bot workflow has been completely redesigned to use **Twilio Content Templates** with **pre-defined static buttons** for menu navigation, following Twilio's WhatsApp constraints.

**Date**: 2026-01-11
**Status**: ✅ Implementation Complete

---

## Key Changes

### ❌ Old Workflow
- Dynamic inline buttons generated at runtime
- AI-driven coaching on every interaction
- Direct "Good morning" → Plan → Outlet coaching flow
- No menu system

### ✅ New Workflow
- **Menu-based navigation** with pre-defined buttons
- **Numbered outlet selection** (outlets shown as text list, not buttons)
- **Greeting menu** as entry point
- **Static buttons** defined in Twilio Content Templates
- Clean separation of menu navigation vs. action nodes

---

## New Files Created

### 1. `src/whatsapp/templates.py` (260 lines)
**Purpose**: Centralized button template configuration
- Defines 3 button templates (greeting, plan_view, help)
- Maps button text to actions
- Provides setup instructions
- Handles template retrieval

### 2. `src/whatsapp/__init__.py` (16 lines)
**Purpose**: Module exports
- Exports template functions and types

### 3. `src/graph/menu_nodes.py` (177 lines)
**Purpose**: Menu navigation nodes
- `greeting_menu_node()` - Main menu (4 buttons)
- `plan_view_menu_node()` - Plan options (3 buttons)
- `show_outlet_list_node()` - Numbered outlet list (NO buttons)
- `show_status_node()` - Show metrics
- `help_menu_node()` - Help menu (4 buttons)

### 4. `TWILIO_SETUP_GUIDE.md` (400+ lines)
**Purpose**: Complete setup documentation
- Step-by-step Twilio Console instructions
- Template configuration details
- Button text mappings
- Troubleshooting guide

### 5. `WORKFLOW_CHANGES_SUMMARY.md` (This file)
**Purpose**: Document all changes made

---

## Modified Files

### 1. `src/graph/state.py`
**Changes**:
- Added `template_type: Optional[str]` field
- Added `menu_context: Optional[str]` field
- Added new state constants:
  - `GREETING_MENU`
  - `PLAN_VIEW_MENU`
  - `OUTLET_SELECT`
- Updated `create_initial_state()` to initialize new fields

### 2. `src/graph/edges.py`
**Changes**:
- Added `BUTTON_TEXT_MAP` dictionary (18 button mappings)
- Completely rewrote `route_user_input()`:
  - Expanded return types to include menu nodes
  - Added button text matching (exact, case-insensitive)
  - Added numeric input detection for outlet selection
  - Changed default from `error` → `greeting_menu`
- Removed unused routing functions

### 3. `src/graph/nodes.py`
**Changes**:
- Updated `outlet_arrival_node()`:
  - Added numeric selection handling
  - Checks if `current_state == OUTLET_SELECT`
  - Maps number to outlet from `daily_plan`
  - Validates selection range

### 4. `src/graph/graph.py`
**Changes**:
- Imported new menu nodes
- Added 5 menu nodes to graph:
  - `greeting_menu`
  - `plan_view_menu`
  - `show_outlet_list`
  - `show_status`
  - `help_menu`
- Updated conditional entry point with 10 routes (was 5)
- Added END edges for all new nodes

### 5. `main.py`
**Changes**:
- Removed old `send_whatsapp_message_with_buttons()` function
- Added new `send_whatsapp_with_template()` function:
  - Uses Content Template SIDs from `src/whatsapp/templates.py`
  - Automatic fallback to plain text if template fails
  - Simpler interface (no manual button handling)
- Updated `process_message_async()`:
  - Gets `template_type` from graph state
  - Passes to `send_whatsapp_with_template()`
- Removed old Content SID constants
- Added better logging

### 6. `.env.example`
**Changes**:
- Added 3 new Content Template SID placeholders:
  - `TWILIO_CONTENT_SID_GREETING`
  - `TWILIO_CONTENT_SID_PLAN_VIEW`
  - `TWILIO_CONTENT_SID_HELP`
- Added reference to TWILIO_SETUP_GUIDE.md

---

## New User Flow

### 1. Greeting
**User**: Hi / Hello / 👋

**System**: Shows greeting menu with 4 buttons:
```
👋 සුභ උදෑසනක් Nalin Perera!

ඔබට අද මොනවා කරන්න ඕනද?

[Buttons]:
1. මගේ අද දවසේ සැලැස්ම
2. මගේ වර්තමාන තත්ත්වය
3. උදව් අවශ්‍යයි
4. අද Check-in කරන්න
```

### 2. View Plan
**User**: Clicks "මගේ අද දවසේ සැලැස්ම"

**System**: Shows plan view menu with 3 buttons:
```
📋 අද දවසේ සැලැස්ම

මුළු Outlets: 3
Priority Outlets: 1 ⭐
Target: LKR 50,000

ඔබට අදට වැදගත් Outlet බලන්න ඕනේ කොහොමද?

[Buttons]:
1. Top 3 Outlet
2. සම්පූර්ණ ලැයිස්තුව
3. නැවත පසුට
```

### 3. Outlet Selection
**User**: Clicks "Top 3 Outlet"

**System**: Shows numbered list (NO buttons):
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

### 4. Outlet Coaching
**User**: Types "1"

**System**: Routes to `outlet_arrival_node()`, provides coaching

### 5. Status Check
**User**: Clicks "මගේ වර්තමාන තත්ත්වය" from greeting menu

**System**: Shows metrics, returns to greeting menu:
```
📊 වර්තමාන තත්ත්වය

අද visit කළ outlets: 2 / 3
Route adherence: 66.7%
මුළු විකුණුම: LKR 28,500

තව outlets visit කරන්න 🚗

[Returns to Greeting Menu with buttons]
```

---

## Button Text Mappings

### Greeting Menu
| Sinhala Text | Action | Routes To |
|-------------|--------|-----------|
| මගේ අද දවසේ සැලැස්ම | show_plan | plan_view_menu |
| මගේ වර්තමාන තත්ත්වය | show_status | show_status |
| උදව් අවශ්‍යයි | show_help | help_menu |
| අද Check-in කරන්න | morning_checkin | morning_checkin |

### Plan View Menu
| Text | Action | Routes To |
|------|--------|-----------|
| Top 3 Outlet | show_top3 | show_outlet_list (top 3) |
| සම්පූර්ණ ලැයිස්තුව | show_full_list | show_outlet_list (all) |
| නැවත පසුට | back_to_greeting | greeting_menu |

### Help Menu
| Text | Action | Routes To |
|------|--------|-----------|
| දවස පටන් ගන්න 🌅 | morning_checkin | morning_checkin |
| Outlet Visit 📍 | help_visit | help_menu (specific help) |
| විකුණුම් Record 💰 | help_sales | help_menu (specific help) |
| නැවත පසුට | back_to_greeting | greeting_menu |

---

## Technical Architecture

### Graph Structure (Before)
```
Entry Point → Conditional Routing → Action Nodes → END
                 ↓
    - morning_checkin
    - outlet_arrival
    - visit_complete
    - end_of_day
    - error_handler
```

### Graph Structure (After)
```
Entry Point → Conditional Routing → Menu/Action Nodes → END
                 ↓
    Menu Nodes:
    - greeting_menu
    - plan_view_menu
    - show_outlet_list
    - show_status
    - help_menu

    Action Nodes:
    - morning_checkin
    - outlet_arrival
    - visit_complete
    - end_of_day
    - error_handler
```

### State Flow
```
IDLE
  ↓ (Hi/Hello)
GREETING_MENU (buttons shown)
  ↓ (Click "මගේ අද දවසේ සැලැස්ම")
PLAN_VIEW_MENU (buttons shown)
  ↓ (Click "Top 3 Outlet")
OUTLET_SELECT (numbered list, no buttons)
  ↓ (Type "1")
AT_OUTLET (coaching provided)
  ↓ (Type "Sales 15000")
ACTIVE
  ↓ (Type "End day")
DAY_COMPLETE
```

---

## Key Design Decisions

### 1. Why Pre-defined Buttons?
**Constraint**: Twilio WhatsApp requires Content Templates for buttons
**Solution**: Create 3 static templates with fixed button text

### 2. Why Numbered Outlet Lists?
**Constraint**: Cannot create buttons dynamically for each outlet
**Solution**: Show outlets as numbered text list, user types number

### 3. Why Greeting Menu First?
**Reason**: Better UX - user chooses what they need instead of being forced into morning check-in

### 4. Why No Buttons on Outlet List?
**Constraint**: WhatsApp limits 3-4 buttons per message, outlets may exceed this
**Solution**: Numbered selection is more scalable

### 5. Why Template Fallback?
**Reason**: System works even without Content Templates configured
**Benefit**: Can test locally without Twilio setup

---

## Testing Strategy

### Without Content Templates
1. Start server: `python main.py`
2. Send "Hi" → Gets plain text menu (no buttons)
3. Type button text manually: "මගේ අද දවසේ සැලැස්ම"
4. System routes correctly
5. All functionality works, just no clickable buttons

### With Content Templates
1. Create templates in Twilio Console (see TWILIO_SETUP_GUIDE.md)
2. Add Content SIDs to `.env`
3. Restart server
4. Send "Hi" → Gets clickable buttons
5. Click buttons instead of typing

---

## Migration Notes

### Breaking Changes
- Old button format no longer works
- State now requires `template_type` and `menu_context`
- Routing function signature changed

### Backward Compatibility
- Old nodes (`morning_checkin`, `outlet_arrival`, etc.) still work
- Can still type "At SD0001" directly
- Can still type "Sales 15000" for recording

### What Users Need to Do
1. Create 3 Content Templates in Twilio Console
2. Add Content SIDs to `.env` file
3. Restart application
4. Test with WhatsApp

---

## Code Statistics

### New Lines Added
- `src/whatsapp/templates.py`: 260 lines
- `src/graph/menu_nodes.py`: 177 lines
- `TWILIO_SETUP_GUIDE.md`: 400+ lines
- **Total**: ~850+ new lines

### Modified Lines
- `src/graph/state.py`: +10 lines
- `src/graph/edges.py`: ~80 lines changed
- `src/graph/nodes.py`: +30 lines
- `src/graph/graph.py`: +20 lines
- `main.py`: ~40 lines changed
- `.env.example`: +7 lines
- **Total**: ~180 lines modified

### Files Added: 5
### Files Modified: 6

---

## Benefits

### For Users (DSRs)
✅ Clearer navigation with visual buttons
✅ Can see all options at once
✅ Less typing required
✅ Intuitive menu structure
✅ Back buttons for easy navigation

### For Developers
✅ Clean separation of concerns (menu vs actions)
✅ Centralized button configuration
✅ Easy to add new menu options
✅ Better testability (can test without Twilio)
✅ Comprehensive documentation

### For System
✅ Follows Twilio's best practices
✅ Scalable menu structure
✅ Works with/without Content Templates
✅ Better error handling
✅ Detailed logging for debugging

---

## Next Steps

### Immediate
1. ✅ Create Content Templates in Twilio Console
2. ✅ Add Content SIDs to `.env`
3. ✅ Test with real WhatsApp number

### Future Enhancements
- Add more menu options (Reports, Settings, etc.)
- Multi-language support (currently Sinhala only)
- Rich media templates (images, documents)
- Call-to-action buttons (phone calls, URLs)

---

## References

- [TWILIO_SETUP_GUIDE.md](TWILIO_SETUP_GUIDE.md) - Detailed setup instructions
- [src/whatsapp/templates.py](src/whatsapp/templates.py) - Button templates code
- [Twilio WhatsApp Buttons Docs](https://www.twilio.com/docs/whatsapp/buttons)

---

**Implementation By**: AI Assistant (Claude Code)
**Approved By**: User
**Date**: 2026-01-11
**Status**: ✅ Complete & Ready for Testing
