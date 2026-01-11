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

## Example Conversation Flow

### Morning Start
**Agent:**
```
Good morning, Nalin!

You've got 3 outlets on your route today. Two of them are priority outlets.
Would you like me to summarize your targets before you start?
```

**DSR:** Yes, please.

**Agent:**
```
Here's your plan for today:

SD0001 – Expected: 12,000 | Last: 13,500 ✅ Ahead of target
SD0002 – Expected: 10,000 | Last: 9,200 ⚠️ Behind target
SD0003 – Expected: 15,000 | Last: 15,800 ✅ Ahead of target

You're performing well in your priority outlets. SD0002 needs a little push.
Would you like a few ideas to improve sales there?
```

**DSR:** Yes, tell me but tell me how to push them?

---

### Coaching Suggestion
**Agent:**
```
You're a top DSR with good communication skills based on your past month coaching scores you've got. So come on you can!

For SD0002, last week's feedback showed lower shelf visibility. You could try:
1. Rechecking product placement
2. Offering the "Buy 5 cases – 1 case free" promo

Want me to remind you when you reach that outlet?
```

**DSR:** Sure, do that.

---

### Prioritization Insight
**Agent:**
```
Focus on SD0003 first, it's a priority outlet and currently 12% behind.
Improving here can quickly boost your daily score.
```

---

### Motivation & Tip
**Agent:**
```
Also, try checking if the store has enough stock of fast-moving SKUs.
If not, upsell 1 more case of the top-performing item from last week.

Would you like me to show which SKU performed best?
```

**DSR:** Yes, that'll help, but same time can you tell me how I can approach this outlet to buy this SKU? I need help?

**Agent:**
```
Orange Crush --> Here are some tips (full detail nice tips short and sweet):

1. Start with rapport - ask how business has been
2. Mention you noticed they're running low on Orange Crush
3. Show data: "This SKU sold 15 units last week - customers love it"
4. Offer the promotion: "Buy 5 cases, get 1 free today only"
5. Create urgency: "Stock is limited for this promo"
6. Ask for commitment: "Shall I add 5 cases to your order?"

Remember: Be confident but not pushy. Listen to their concerns.
```

---

### End of Day Wrap Up (Agent - Wrap up)
**Agent:**
```
You've completed all assigned outlets today.

2 outlets ahead of target, 1 slightly behind.
Overall, your target achievement rate is 96% - well done!

Would you like to review tomorrow's plan?
```

**DSR:** Sure, let's do that tomorrow morning.

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
