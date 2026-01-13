# Twilio WhatsApp Button Setup Guide

Complete guide to creating interactive WhatsApp buttons using Twilio Content Templates.

---

## Overview

WhatsApp allows **MAX 3 Quick Reply buttons** for unapproved session templates. Our application uses 3 content templates with different button configurations for different conversation stages.

---

## Prerequisites

1. Twilio Account with WhatsApp enabled
2. WhatsApp Sandbox setup (or approved WhatsApp Business Account)
3. Account SID and Auth Token from Twilio Console

---

## Step 1: Access Content Template Builder

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to **Messaging** > **Content Template Builder**
3. Click **Create new Template**

---

## Step 2: Create the 3 Required Templates

### Template 1: Greeting Menu

**Purpose:** Main menu shown when user says Hi/Hello or after most actions

**Configuration:**
- **Template Name:** `greeting_menu`
- **Template Type:** `Quick Reply`
- **Language:** `English` (or `Sinhala` if available)
- **Content Type:** `Text`

**Body:**
```
{{1}}
```

**Buttons (3 Quick Reply buttons):**

| Button ID | Button Text | Payload/Action |
|-----------|-------------|----------------|
| `checkin` | `Check-in 🌅` | CHECKIN |
| `outlet_details` | `Outlet විස්තර 📍` | OUTLET_DETAILS |
| `end_summary` | `දවස අවසානය 🌙` | END_SUMMARY |

**Steps:**
1. Click "Add Quick Reply Button"
2. Enter Button ID: `checkin`
3. Enter Display Text: `Check-in 🌅`
4. Repeat for other 2 buttons
5. Click **Submit for Approval** (or **Save** if in sandbox mode)

**After creation:**
- Copy the **Content SID** (starts with `HX...`)
- Add to `.env`: `TWILIO_CONTENT_SID_GREETING=HX...`

---

### Template 2: Area View

**Purpose:** Shown after check-in or when viewing outlets by area

**Configuration:**
- **Template Name:** `area_view`
- **Template Type:** `Quick Reply`
- **Language:** `English` (or `Sinhala` if available)
- **Content Type:** `Text`

**Body:**
```
{{1}}
```

**Buttons (3 Quick Reply buttons):**

| Button ID | Button Text | Payload/Action |
|-----------|-------------|----------------|
| `area_view` | `ප්‍රදේශ අනුව 🗺️` | AREA_VIEW |
| `outlet_details` | `Outlet විස්තර 📍` | OUTLET_DETAILS |
| `end_summary` | `දවස අවසානය 🌙` | END_SUMMARY |

**Steps:**
1. Click "Add Quick Reply Button"
2. Enter Button ID: `area_view`
3. Enter Display Text: `ප්‍රදේශ අනුව 🗺️`
4. Repeat for other 2 buttons
5. Click **Submit for Approval** (or **Save** if in sandbox mode)

**After creation:**
- Copy the **Content SID** (starts with `HX...`)
- Add to `.env`: `TWILIO_CONTENT_SID_AREA_VIEW=HX...`

---

### Template 3: Help Menu

**Purpose:** Shown when user needs help or types "help"

**Configuration:**
- **Template Name:** `help_menu`
- **Template Type:** `Quick Reply`
- **Language:** `English` (or `Sinhala` if available)
- **Content Type:** `Text`

**Body:**
```
{{1}}
```

**Buttons (3 Quick Reply buttons):**

| Button ID | Button Text | Payload/Action |
|-----------|-------------|----------------|
| `checkin` | `Check-in 🌅` | CHECKIN |
| `outlet_details` | `Outlet විස්තර 📍` | OUTLET_DETAILS |
| `back` | `ආපසු 🔙` | BACK |

**Steps:**
1. Click "Add Quick Reply Button"
2. Enter Button ID: `checkin`
3. Enter Display Text: `Check-in 🌅`
4. Repeat for other 2 buttons
5. Click **Submit for Approval** (or **Save** if in sandbox mode)

**After creation:**
- Copy the **Content SID** (starts with `HX...`)
- Add to `.env`: `TWILIO_CONTENT_SID_HELP=HX...`

---

## Step 3: Update Environment Variables

After creating all 3 templates, update your `.env` file:

```bash
# Twilio Content Template SIDs
TWILIO_CONTENT_SID_GREETING=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_AREA_VIEW=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_CONTENT_SID_HELP=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Enable Content Templates
USE_CONTENT_TEMPLATES=true
```

Replace the `HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` with your actual Content SIDs from Twilio Console.

---

## Step 4: Test the Buttons

1. Start your FastAPI server:
   ```bash
   python main.py
   ```

2. Send a message to your WhatsApp sandbox number

3. You should see interactive buttons appear based on the conversation flow

---

## Important Notes

### WhatsApp Button Limitations

- ✅ **Max 3 Quick Reply buttons** for unapproved templates
- ✅ **Button text max 20 characters** (emojis count as 1-2 chars)
- ✅ **Emojis are allowed** in button text
- ✅ **Quick Reply buttons work in sandbox** without approval
- ❌ **Cannot have dynamic buttons** - must be predefined in template
- ❌ **Cannot have more than 3 buttons** in unapproved templates

### Template Body Variable

- The body text uses `{{1}}` as a placeholder for dynamic content
- Your application sends the actual message text at runtime
- This allows one template to show different messages

### Fallback to Plain Text

If Content Templates are not configured or fail:
- Set `USE_CONTENT_TEMPLATES=false` in `.env`
- The app will send plain text with button hints instead
- Users can reply with numbers (1, 2, 3) or text

---

## Troubleshooting

### Error 63013: Policy Violation

**Cause:** Message content format violates WhatsApp policies

**Solutions:**
- Remove excessive emojis from message text
- Remove double newlines
- Keep message text clean and simple
- Check for special characters

### Buttons Not Appearing

**Solutions:**
1. Verify Content SIDs are correct in `.env`
2. Check if templates are approved (or using sandbox)
3. Ensure `USE_CONTENT_TEMPLATES=true`
4. Check Twilio logs for errors
5. Verify button IDs match exactly (case-sensitive)

### Wrong Button Actions

**Solutions:**
1. Check button payloads match action names in code
2. Verify button IDs are unique
3. Check logs for button click handling

---

## Testing Checklist

- [ ] All 3 templates created in Twilio Console
- [ ] Content SIDs copied to `.env` file
- [ ] `USE_CONTENT_TEMPLATES=true` set in `.env`
- [ ] Server started without errors
- [ ] WhatsApp connection working
- [ ] Greeting menu shows 3 buttons
- [ ] Buttons are clickable
- [ ] Button clicks trigger correct actions
- [ ] Messages show proper Sinhala text

---

## Alternative: Plain Text Mode

If you prefer not to use Content Templates, you can run in plain text mode:

1. Set `USE_CONTENT_TEMPLATES=false` in `.env`
2. Users will see text hints like:
   ```
   📱 Reply with:
   • "1" - Check-in
   • "2" - Outlet විස්තර
   • "3" - දවස අවසානය
   ```
3. Users can reply with numbers or keywords

---

## Support

- Twilio Documentation: https://www.twilio.com/docs/content-api
- WhatsApp Business API: https://www.twilio.com/docs/whatsapp
- Content Template Builder: https://console.twilio.com/us1/develop/sms/content-template-builder

---

**Last Updated:** 2026-01-13
**Status:** Ready for implementation
