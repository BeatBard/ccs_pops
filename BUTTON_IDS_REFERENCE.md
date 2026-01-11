# Button IDs Quick Reference

Use this as a reference when creating Content Templates in Twilio Console.

⚠️ **IMPORTANT**: WhatsApp allows **MAX 3 buttons** for unapproved session templates!

---

## Template 1: Greeting Menu (`greeting_menu`)

**Content SID Environment Variable**: `TWILIO_CONTENT_SID_GREETING`

| Button # | Button Text | Button ID |
|----------|-------------|-----------|
| 1 | මගේ සැලැස්ම 📋 | `my_plan` |
| 2 | තත්ත්වය 📊 | `my_status` |
| 3 | Check-in ✅ | `checkin` |

---

## Template 2: Plan View Options (`plan_view_options`)

**Content SID Environment Variable**: `TWILIO_CONTENT_SID_PLAN_VIEW`

| Button # | Button Text | Button ID |
|----------|-------------|-----------|
| 1 | ප්‍රමුඛ 3 📍 | `top3` |
| 2 | සම්පූර්ණ ලැයිස්තුව | `full_list` |
| 3 | ආපසු 🔙 | `back` |

---

## Template 3: Help Menu (`help_menu`)

**Content SID Environment Variable**: `TWILIO_CONTENT_SID_HELP`

| Button # | Button Text | Button ID |
|----------|-------------|-----------|
| 1 | දවස පටන් ගන්න 🌅 | `morning` |
| 2 | Outlet යන්න 📍 | `visit` |
| 3 | විකුණුම් ලියන්න 💰 | `record` |

---

## Common Settings for All Templates

- **Template Type**: Quick Reply
- **Body Content**: `{{1}}` (allows dynamic message text)
- **Template Language**: Sinhala (`si`)
- **Max Buttons**: 3 (WhatsApp Sandbox limitation)
- **Button Text Max**: 20 characters

---

## Notes

- **Button Text**: Visible to user, must match exactly (including emojis)
- **Button ID**: Internal identifier, not visible to user
- Copy the **Content SID** (starts with `HX...`) after creating each template
- Add all three Content SIDs to your `.env` file
- Users can type "help" or "උදව්" to access help menu
- Users can type "hi" or "ආපසු" to return to main menu
