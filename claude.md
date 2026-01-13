# Sales Insights and Coaching Assistant - CCS POPS

## Project Overview

Improving CCS frontline sales team capabilities and outcomes with an AI-powered Sales Insights and Coaching Assistant delivered via WhatsApp.

---

## Summary (i1 template)

### Business Problem
- Currently DSRs performance varies and high effort is needed to follow up on key metrics
- Limited in person coaching opportunities to develop the DSR skills

### Analytical Solution
- Develop a situational and location-specific decision-support system for DSRs
- The system provides personalized nudges, reminders, and insights based on outlet type, visit history, and territory characteristics

### Sources of Value/Methodology
- **Productivity lift** through improved route adherence, higher productive visit ratio, and better outlet coverage
- **Sales growth** via improved SKU range selling and targeted upselling based on outlet profile

---

## What We Want from the Tool/Agentic Solution

## Capabilities of a Perfect DSR

| Capability | Outcome | Metric | How AI Support Helps |
|------------|---------|--------|----------------------|
| Visits outlets more often | Volume growth, better outlet-rep relationship | Higher route adherence | Pre-shift & end-of-day check-ins – Remind planned outlets, track visits, and re-plan missed ones |
| Convert at least 90% of visits to productive visits | Volume growth | Higher route productivity | Productivity prompts – Quick visit checklist and follow-up tips to boost conversions |
| Convinces outlet to buy | Volume growth | Higher productive visits | Offer nudges – Suggest incentives, cross-sells, and confirm conversion status |
| Covers more new outlets | Improve outlet coverage | Outlet base growth | New outlet alerts – Flag nearby unvisited outlets and track first-visit outcomes |
| Covers existing outlets with higher productive visits | Higher incremental margin | Margin growth | Repeat-visit planning – Remind high-potential outlets and recap margin impact |
| Visits more high performing outlets | Consistent-reliable buying patterns | Mid 50 outlet volume growth | Top outlet focus – Nudge to revisit top 50 outlets; track response and growth |
| Sells and covers a higher SKU range | Higher LIPB | LIPB and Mid 50 LIPB | SKU cross-sell tips – Post-visit SKU prompts with quick product refresher |
| Plans outlet offtake | Consistent purchases due to planning | Smooth purchase pattern | Reorder reminders – Suggest reorder quantities and confirm before stockouts |
| Sets outlet for optimum visibility | Improves cooler maintenance quality | Cooler volumes | Visibility checks – Photo-based planogram reminders and corrective follow-ups |

---

## Day in a DSR's Life - Intervention Points

### Morning (8:30 AM) - Route Planning
**Type:** Recurring
**Coaching/Intervention:**
Nudge: "Good morning! You have 12 outlets planned today. 3 are high-potential but missed last week – add them first to improve route adherence."

**Data Sources:**
- Pre-prepared 'Key Focus Outlets' table
- Progress of sales vs target

**Prompt Logic:**
Return the high potential outlets from today's route that were not visited last week - and potential target volume.

---

### During Visit (10:15 AM) - At First Outlet
**Type:** Recurring
**Coaching/Intervention:**
"This outlet's Avg LIPB is 2. Last time they bought only 1 SKU. Try adding SKU X — similar outlets increased volume by 15%."

**Data Sources:**
- Dataframe: DSR | outlet | LIPB
- Dataframe: outlet | top 5 selling SKUs of outlets in adjacent routes
  - *(Need to come up with a method to find the adjacent routes)*

**Prompt Logic:**
Return the average LIPB of selected outlets and top 5 fast moving SKUs of the outlets of adjacent routes.

---

### Midday (12:45 PM) - New Outlet Alert
**Type:** Ad hoc
**Coaching/Intervention:**
"New outlet alert! Here's its profile: near 3 schools, moderate traffic, fast-moving SKUs are Y and Z. Try offering…"

**Data Sources:**
- Dataframe: outlet | POI places
  - *(Need to come up with a method to assign POI places for each outlet)*
- Dataframe: outlet | top 5 selling SKUs of outlets in adjacent routes

**Prompt Logic:**
Return the POI places for the selected outlets and top 5 fast moving SKUs of the outlets of adjacent routes.

---

### Afternoon (3:30 PM) - Sales Dip Alert
**Type:** Ad hoc
**Coaching/Intervention:**
Alert: "This outlet's offtake dropped 25% vs. last month. Ask if cooler is working properly and check stock of fast-moving SKUs."

**Data Sources:**
- Dataframe: year_month | outlet | sales volume | past month sales volume | drop/increase since last month

**Prompt Logic:**
If there's a sales drop in previous month, return the sales drop percentage.

---

### Evening (6:00 PM) - End of Day Summary
**Type:** Recurring
**Coaching/Intervention:**
"You covered 9 outlets, 7 productive visits (78%). Great progress! 3 missed outlets rescheduled for tomorrow. Aim for +1 productive visit to hit your weekly goal."

**Data Sources:**
- 'Key Focus Outlets' table with columns: how many covered and sales volume

---

## Phase 1 - What We Will Build

### Channel
**WhatsApp Assistant**
- Sinhala language only (clear, conversational)
- Human-like interactions

### Language Style
**Sinhala text responsive chat space**
- Example: "ඔයා අද කොච්චර outlet cover කරාද?"
- Natural, conversational Sinhala

### Conversations
**3 Fixed Flows:**
1. Morning check-in
2. Mid-day update
3. End-day summary

### Inputs
**Button-based interactions:**
- Numbers
- Yes/No
- Reasons
- Clickables for easy interaction

### Sample Morning Flow

**Agent:**
```
සුභ උදෑසනක්
අද වැඩ පටන් ගන්න ready ද?
```

**Clickables:** `OW` | `NA` | `ADA LEAVE`

**Agent Status Display:**
```
අද status එක මෙන්න

Plan කරපු outlets: 28
Cover කරපු outlets: 17
ඉතුරු: 11

Breakdown:
Eatery: 5 | SMMT: 3
```

### Insights
**Rule-based:**
- Covered vs planned
- Missed outlets by category

### Route Logic
**Text nudges:**
- Simple Sinhala tips
- **Behavior shaping ---> WHOLE POINT OF SFE**

### Coaching
**WhatsApp buttons:**
- Maximum 3–4 buttons per step

### UI
**Technology:**
- WhatsApp API
- Simple backend (FastAPI)

---

## Core Capabilities - Phase 1

### 1. Start of Day
✅ Start day conversation with "සුභ උදෑසනක්, අද වැඩ පටන් ගන්න ready ද?"
✅ Answer via clickables: `OW` | `NA` | `ADA LEAVE`

### 2. Communicate Status
**Main cards on the front page should be:**
✅ Give summary of day's plan
✅ Outlets count
✅ Areas
✅ Types of outlets

### 3. Real-time Tracking
✅ Track and update with real-time outlets covered vs planned
✅ Communicate status of the day (same metrics tracking)

### 4. Route Adherence
✅ Measure adherence of the plan as a percentage
✅ Assess the route followed **OR** suggest routes based on outlets left/remaining
✅ Provide measure of outlets remaining to visit and types

### 5. SKU Intelligence
✅ Tell which SKUs are best selling in an area
✅ Provide % of SKUs left to cover

### 6. Proactive Alerts
✅ Flag any issues or poor visiting plans *(sub buttons)*
✅ Exceptional reminders/nudges - "too slow today, missed 2 priority outlets today"

### 7. Coaching & Motivation
✅ Send messages on selling tips/negotiation specific to DSR
✅ Send messages specific to outlets of the DSR (area, type of outlets on day's target list)
✅ Send constant nudges and motivational messages specific to DSR (based on strength area/volume history)
✅ Communicate on seasonal sales (e.g., Christmas)

### 8. End of Day
✅ Summarize the end of the day
✅ Minimal typing but many clickables

---

## Updated Conversation Flow (Phase 1 - POC)

### Flow Overview
The conversation follows a **3-button navigation pattern** throughout, with context-aware responses:
1. **Check-in 🌅** - Start the day and view plan
2. **Outlet විස්තර 📍** - View outlet characteristics and get coaching
3. **දවස අවසානය 🌙** - End of day summary

---

## Detailed Flow with Examples

### 1️⃣ Initial Greeting (Entry Point)
**Trigger:** User sends "Hi", "Hello", "හායි", "හෙලෝ", or any greeting

**Agent Response:**
```
👋 සුභ උදෑසනක් [DSR Name]!

මම ඔබේ *Pocket Coach* 🎯

ඔබේ දවසේ සෑම අවස්ථාවකම ඔබට උදව් කරන්න මම සූදානම්!

මම ඔබට කරන්න පුළුවන්:
• දවස Check-in කරන්න සහ plan එක බලන්න
• Outlet විස්තර සහ coaching ලබා ගන්න
• දවසේ summary එක බලන්න

ඔබට අද මොනවා කරන්න ඕනද? 💪
```

**Buttons:**
1. ✅ Check-in 🌅
2. 📍 Outlet විස්තර
3. 🌙 දවස අවසානය

---

### 2️⃣ Check-in Flow (Button 1: Check-in 🌅)

**Agent Response:**
```
🌅 *අද දවසේ සැලැස්ම*

📊 අද ඔබේ Plan එක:
• මුළු Outlets: 10
• Priority Outlets: 5 ⭐
• Outlet වර්ග: SMMT (5), Eatery (3), Non-Eatery (2)
• ප්‍රදේශ: Nugegoda, Maharagama, Pannipitiya, Kottawa, Dehiwala

🎯 අද දවසේ Target: 105,000L

හොඳ දවසක් ගත කරන්න! ඔබ කැමති මොනවාද බලන්න? 🚀
```

**Buttons:**
1. 🗺️ ප්‍රදේශ අනුව Outlets
2. 📍 Outlet විස්තර
3. 🌙 දවස අවසානය

---

### 3️⃣ Area-wise Outlets (Button 1: ප්‍රදේශ අනුව Outlets)

**Agent Response:**
```
🗺️ *ප්‍රදේශ අනුව Outlets*

📍 *Nugegoda* (2 Outlets)
1. ⭐ Saman's Mart (SMMT) - Target: 12,000L
   📌 https://maps.google.com/?q=6.8774,79.8892

2. City Bites Cafe (Eatery) - Target: 10,000L
   📌 https://maps.google.com/?q=6.8774,79.8892

---

📍 *Maharagama* (1 Outlet)
3. ⭐ Perera Super (SMMT) - Target: 15,000L
   📌 https://maps.google.com/?q=6.8488,79.9267

---

📍 *Kottawa* (1 Outlet)
4. Quick Snacks (Eatery) - Target: 8,000L
   📌 https://maps.google.com/?q=6.8108,79.9614

Outlet විස්තර බලන්න outlet number එක type කරන්න (උදා: 1) 👇
```

**Buttons:**
1. 🗺️ ප්‍රදේශ අනුව Outlets
2. 📍 Outlet විස්තර
3. 🌙 දවස අවසානය

---

### 4️⃣ Outlet Characteristics Flow (Button 2: Outlet විස්තර)

#### Step 4A: Request Outlet Number
**Agent Response:**
```
📍 *Outlet විස්තර*

කරුණාකර ඔබට විස්තර බලන්න ඕන outlet එකේ number එක type කරන්න:

උදාහරණය: 1 (Saman's Mart සඳහා)

ඔබේ අද දවසේ outlets:
1. ⭐ Saman's Mart (Nugegoda)
2. ⭐ City Bites Cafe (Maharagama)
3. ⭐ Perera Super (Pannipitiya)
4. Quick Snacks (Kottawa)
5. Lanka Stores (Dehiwala)
...
```

**User types:** `1`

---

#### Step 4B: Message 1 - Outlet Statistics
**Agent Response:**
```
📊 *Saman's Mart - SMMT Outlet*

🏪 *Outlet විස්තර:*
• වර්ගය: SMMT (Supermarket)
• ප්‍රදේශය: Nugegoda
• Priority: ⭐ ඉහළ

📈 *විකුණුම් දත්ත:*
• අද Target: 12,000L
• පසුගිය visit: 13,500L ✅ (Target අතිරේකයි)
• අවසන් මාස 3 සාමාන්‍යය: 12,800L/visit
• මාසික Target: 150,000L
• මාසික සම්පූර්ණ කළ ප්‍රමාණය: 85,000L (56.7%)

🔝 *වඩාත්ම විකුණෙන භාණ්ඩ:*
1. Coca-Cola 1L - 850L/visit
2. Sprite 1L - 620L/visit
3. Fanta Orange 1L - 480L/visit

💡 *විශේෂ සටහන:*
• Cooler ඇත: ✅ Yes
• Shelf space: 12.5 sqft
• ප්‍රදේශය: Schools, Bus Stop, Bank අසල
```

---

#### Step 4C: Message 2 - AI-Generated Coaching
**Agent Response (AI-Generated in Sinhala):**
```
💡 *Coaching Tips - Gemini AI*

මේ outlet එක හොඳට perform කරනවා! 👏

✨ *අද උත්සාහ කරන්න:*

• Coca-Cola සහ Sprite හොඳට විකුණෙනවා - අද Fanta variety 2-3ක් add කරන්න try කරන්න

• Schools අසල නිසා, පොඩි bottles (200ml-400ml) promote කරන්න - school children ට හොඳයි

• පසුගිය visit එකේ target එක ඉක්මවලා - අද හොඳ relationship එකක් තියෙනවා කතා කරන්න easy

• පොඩි offer එකක් දෙන්න: 5 cases ගත්තොත් 1 case free - මාසික target complete කරන්න help කරයි

ඔබට හැකියි! 💪 Customer handling skills use කරලා සාර්ථක visit එකක් කරන්න!
```

**Buttons:**
1. 🗺️ ප්‍රදේශ අනුව Outlets
2. 📍 Outlet විස්තර
3. 🌙 දවස අවසානය

---

### 5️⃣ End of Day Summary (Button 3: දවස අවසානය)

**Agent Response:**
```
🌙 *අද දවසේ Summary*

🎯 *ඔබේ Performance:*

📊 *සාරාංශය:*
• Visit කළ Outlets: 8 / 10
• සැලැස්ම සපුරා ගැනීම: 80%
• Priority Outlets Covered: 4 / 5 ⭐
• සාර්ථක Visits: 7 (87.5%)

💰 *විකුණුම්:*
• අද මුළු විකුණුම: 92,500L
• අද Target: 105,000L
• ඉලක්ක සපුරා ගැනීම: 88.1%

📈 *Outlets Performance:*
• Target අතිරේක: 5 outlets ✅
• Target අඩු: 2 outlets ⚠️
• Visit නොකළ: 2 outlets

🏆 *වර්ධනය:*
• ඊයේට වඩා: +15% ⬆️
• සතිය සාමාන්‍යය: +8% ⬆️

---

💡 *හෙට දිනය සඳහා:*
අද visit නොකළ 2 outlets හෙට plan කරන්න:
• Lanka Stores (Dehiwala) - 9,000L Target
• Fresh Foods (Mount Lavinia) - 11,000L Target

හොඳ කොටස! අද හොඳට perform කළා! 👏
හෙට තව හොඳට කරමු! විශ්‍රාම ගන්න. 😊💪
```

**Buttons:**
1. ✅ Check-in 🌅
2. 📍 Outlet විස්තර
3. 🌙 දවස අවසානය

---

## Key Features of New Flow

### ✅ Navigation Pattern
- **Consistent 3-button navigation** throughout the entire flow
- Context-aware button behavior (e.g., "Outlet විස්තර" asks for number after area view)
- Users can move between any section at any time

### ✅ Sinhala + Emojis
- All text in natural, conversational Sinhala
- Emojis used throughout for visual appeal and clarity
- Technical terms avoided - simple language only

### ✅ Metrics in Litres
- All sales figures shown in litres (L)
- Clear, consistent formatting (e.g., "12,000L")
- Percentage completion for targets

### ✅ Google Maps Integration
- Direct Google Maps links for each outlet
- Format: `https://maps.google.com/?q=latitude,longitude`
- Easy navigation for DSRs in the field

### ✅ Priority Indicators
- Star icon (⭐) for priority outlets
- Visual distinction throughout the flow
- Helps DSRs prioritize their visits

### ✅ AI-Generated Coaching
- Uses Gemini 2.0 Flash for coaching generation
- Context-aware tips based on outlet performance
- Personalized, actionable advice in Sinhala
- Encourages DSRs with positive reinforcement

---

## Button Flow Summary

```
┌─────────────────────────┐
│   Initial Greeting      │
│  (Hi/Hello/හායි/හෙලෝ)  │
└────────┬────────────────┘
         │
    ┌────▼────┐
    │ Welcome │
    │ Message │
    └────┬────┘
         │
    ┌────▼─────────────────────────┐
    │  [Check-in] [Outlet] [End]  │
    └─┬──────────┬────────────┬────┘
      │          │            │
      │          │            └─────► End Summary
      │          │                    [Check-in] [Outlet] [End]
      │          │
      │          └────────────────► Outlet විස්තර
      │                             (Ask for outlet #)
      │                             ↓
      │                             Statistics + AI Coaching
      │                             [Area] [Outlet] [End]
      │
      └─────────────────────────► Check-in Plan
                                  ↓
                                  [Area] [Outlet] [End]
                                  ↓
                                  Area-wise Outlets
                                  [Area] [Outlet] [End]
```

---

## Technical Architecture

### Backend
- **Framework:** FastAPI
- **Database:** TBD (for outlet data, DSR performance, SKU data)
- **AI Engine:** Google Gemini 3 Flash Preview

### Communication Channel
- **Platform:** Twilio WhatsApp API
- **Webhook:** FastAPI endpoint receiving incoming messages
- **Response:** TwiML for structured WhatsApp messages

### Data Requirements

#### Tables/DataFrames Needed:
1. **Key Focus Outlets**
   - DSR_ID | Outlet_ID | Planned_Date | Visit_Status | Sales_Target | Last_Visit_Sales

2. **DSR Outlet LIPB**
   - DSR_ID | Outlet_ID | LIPB | Avg_LIPB | Last_Visit_SKU_Count

3. **Outlet SKU Performance**
   - Outlet_ID | SKU_ID | Sales_Volume | Rank | Adjacent_Route_Performance

4. **Outlet POI (Points of Interest)**
   - Outlet_ID | POI_Type | Distance | POI_Name

5. **Sales History**
   - Year_Month | Outlet_ID | Sales_Volume | Previous_Month_Volume | Percentage_Change

6. **DSR Performance**
   - DSR_ID | Date | Outlets_Planned | Outlets_Covered | Productive_Visits | Route_Adherence_Percentage

7. **Coaching Scores**
   - DSR_ID | Month | Communication_Score | Negotiation_Score | Strengths | Areas_To_Improve

---

## Key Metrics to Track

1. **Route Adherence %** = (Outlets Covered / Outlets Planned) × 100
2. **Productive Visit Ratio** = (Productive Visits / Total Visits) × 100
3. **LIPB (Lines in Primary Billing)** = Number of SKUs sold per visit
4. **Mid 50 Outlet Volume Growth** = Volume increase in top 50 outlets
5. **Target Achievement Rate** = (Actual Sales / Target Sales) × 100
6. **Outlet Coverage** = New outlets added to route
7. **SKU Range Coverage** = Unique SKUs sold across all outlets

---

## Implementation Phases

### Phase 1 (Current)
- WhatsApp integration
- 3 fixed conversation flows (Morning, Midday, Evening)
- Sinhala language support
- Button-based interactions
- Rule-based insights

### Phase 2 (Future)
- AI-powered personalized coaching
- Photo-based planogram verification
- Real-time location-based nudges
- Predictive analytics for outlet performance
- Multi-language support

### Phase 3 (Future)
- Manager dashboard
- Team performance analytics
- Advanced route optimization
- Integration with CRM/ERP systems

---

## Success Criteria

### Quantitative
- Route adherence improves to 90%+
- Productive visit ratio increases to 90%+
- LIPB increases by 20%
- Mid 50 outlet volume growth of 15%+
- Target achievement rate of 95%+

### Qualitative
- DSRs feel more confident during visits
- Reduced time spent on manual planning
- Better coaching coverage across all DSRs
- Improved DSR satisfaction scores

---

## Project Status

**Current Phase:** Phase 1 - Foundation Setup

**Completed:**
- ✅ WhatsApp integration with Twilio
- ✅ Basic webhook endpoint
- ✅ Google Gemini AI integration
- ✅ Environment configuration

**Next Steps:**
- [ ] Design conversation flows in Sinhala
- [ ] Create data schemas and mock data
- [ ] Implement morning check-in flow
- [ ] Implement real-time tracking
- [ ] Add coaching prompt system
- [ ] Test with sample DSRs

---

## Notes

- All interactions should be in **Sinhala** for Phase 1
- Focus on **minimal typing, maximum clicking** for DSR ease of use
- Keep messages **short and actionable**
- Provide **context-aware coaching** based on DSR performance history
- Use **positive reinforcement** and motivation

---

**Last Updated:** 2026-01-11
**Project Owner:** CCS POPS Team
**Technical Lead:** TBD
