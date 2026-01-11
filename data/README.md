# Mock Data for CCS POPS POC - Nalin Perera

This folder contains mock datasets for testing the Sales Insights and Coaching Assistant POC focused on DSR **Nalin Perera**.

## Dataset Overview

### 1. sku_master.csv
**Purpose:** Master list of all SKUs (products) available

**Columns:**
- `sku_id`: Unique SKU identifier
- `sku_name`: Product name
- `category`: Product category (Carbonated Soft Drinks, Water, Juice)
- `price`: Product price in LKR
- `promo_available`: Whether a promotion is currently running (Yes/No)
- `promo_description`: Details of the promotion

**Use Cases:**
- Show available SKUs to DSR
- Display promotions for upselling
- SKU recommendations

---

### 2. outlet_details.csv
**Purpose:** Detailed information about outlets including location and POI data

**Columns:**
- `outlet_id`: Unique outlet identifier
- `outlet_name`: Name of the outlet
- `outlet_type`: Type (SMMT, Eatery, Non-Eatery)
- `area`: Location area
- `district`: District name
- `poi_nearby`: Points of Interest nearby (Schools, Hospitals, etc.) separated by |
- `poi_count`: Number of POIs nearby
- `traffic_level`: Foot traffic level (High, Medium, Low)
- `cooler_available`: Whether outlet has a cooler (Yes/No)
- `shelf_space_sqft`: Available shelf space in square feet

**Use Cases:**
- Outlet profiling for new outlet alerts
- Understanding outlet context for coaching
- POI-based recommendations

**Nalin's Outlets:**
- SD0001: Saman's Mart (SMMT, Nugegoda)
- SD0002: City Bites Cafe (Eatery, Maharagama)
- SD0003: Perera Super (SMMT, Pannipitiya)
- SD0016: Quick Snacks (Eatery, Kottawa)

---

### 3. visit_history.csv
**Purpose:** Historical record of all visits by DSRs to outlets

**Columns:**
- `dsr_name`: Name of DSR
- `outlet_id`: Outlet visited
- `visit_date`: Date of visit
- `visit_time`: Time of visit
- `lipb`: Lines in Primary Billing (number of SKUs sold)
- `sku_count`: Number of unique SKUs sold
- `sales_value`: Total sales value in LKR
- `productive_visit`: Whether visit resulted in sales (Yes/No)
- `visit_duration_mins`: Duration of visit in minutes
- `notes`: Any notes from the visit

**Use Cases:**
- Track LIPB trends
- Identify visit patterns
- Compare current vs. past performance
- Generate coaching insights

---

### 4. sku_performance_by_outlet.csv
**Purpose:** SKU-level sales performance at each outlet

**Columns:**
- `outlet_id`: Outlet identifier
- `sku_id`: SKU identifier
- `sku_name`: SKU name
- `sales_last_week`: Units sold last week
- `sales_last_month`: Units sold last month
- `rank`: Performance rank (1 = best seller)
- `stock_status`: Current stock status (In Stock, Low Stock, Out of Stock)
- `avg_weekly_sales`: Average weekly sales

**Use Cases:**
- Top SKU recommendations
- Cross-selling suggestions
- Stock alerts
- Identify fast-moving SKUs

**Key Insights:**
- SD0001: Coca-Cola 500ml is #1 (45 units/week)
- SD0002: Has visibility issues, Fanta is out of stock
- SD0003: Best performing outlet overall
- SD0016: Lower volume, stock issues

---

### 5. daily_plan.csv
**Purpose:** Daily plan of outlets to visit

**Columns:**
- `dsr_name`: Name of DSR
- `date`: Plan date
- `outlet_id`: Outlet to visit
- `outlet_name`: Outlet name
- `outlet_type`: Type of outlet
- `priority`: Priority outlet (Yes/No)
- `target_sales`: Target sales for the day
- `last_visit_sales`: Sales from last visit
- `status`: Visit status (Pending, Completed, Missed)
- `visit_order`: Suggested visit sequence
- `completed`: Whether visit is completed (Yes/No)

**Use Cases:**
- Morning check-in summary
- Track progress during day
- End of day recap
- Calculate route adherence

**Today's Plan (2026-01-11):**
- 3 outlets planned for Nalin
- 2 priority outlets (SD0001, SD0003)
- Total target: 37,000 LKR

---

### 6. lipb_tracking.csv
**Purpose:** Track LIPB (Lines in Primary Billing) performance per outlet

**Columns:**
- `dsr_name`: Name of DSR
- `outlet_id`: Outlet identifier
- `avg_lipb`: Average LIPB for the month
- `last_lipb`: LIPB from last visit
- `target_lipb`: Target LIPB
- `lipb_trend`: Trend (Improving, Stable, Declining)
- `month`: Month of tracking

**Use Cases:**
- LIPB coaching and improvement tracking
- Identify outlets needing SKU range expansion
- Performance monitoring

**Nalin's Performance:**
- SD0001: Avg LIPB 3.0 (Target: 4) - Stable
- SD0002: Avg LIPB 1.3 (Target: 3) - **Declining** ⚠️
- SD0003: Avg LIPB 4.0 (Target: 4) - Improving ✅
- SD0016: Avg LIPB 1.7 (Target: 3) - Stable

---

### 7. coaching_tips.csv
**Purpose:** Library of coaching tips in Sinhala and English

**Columns:**
- `tip_id`: Unique tip identifier
- `category`: Tip category (Upselling, Shelf Visibility, Promotion, etc.)
- `situation`: When to use this tip
- `tip_sinhala`: Tip in Sinhala language
- `tip_english`: Tip in English language
- `strength_area`: Related strength area
- `development_area`: Related development area

**Use Cases:**
- Contextual coaching during visits
- Personalized tips based on DSR strengths/weaknesses
- Situation-specific guidance
- Sinhala language support

**Categories:**
- Upselling
- Shelf Visibility
- Promotion
- Timing
- Stock Management
- Relationship Building
- Seasonal Sales
- Performance Recognition

---

## Integration with Existing Data

### From data.csv (Row for Nalin Perera):
```
sku_focus_progress: 91%
volume_per_outlet: 62,279
current_festive_season: Christmas
strength_areas: Customer Handling
development_areas: Route Planning
preferred_checkin_time: 10:00 AM
response_rate_to_coach: 93%
```

### From outlet.csv (Nalin's outlets):
```
SD0001: Expected 12,000 | Actual 13,500 (Ahead)
SD0002: Expected 10,000 | Actual 9,200 (Behind)
SD0003: Expected 15,000 | Actual 15,800 (Ahead)
SD0016: Expected 9,000 | Actual 8,300 (Behind)
```

---

## Data Relationships

```
daily_plan.csv
    ↓ (outlet_id)
outlet_details.csv ← visit_history.csv
    ↓ (outlet_id)        ↓ (lipb)
sku_performance_by_outlet.csv → lipb_tracking.csv
    ↓ (sku_id)
sku_master.csv → coaching_tips.csv
```

---

## Usage Examples

### Morning Check-in
```python
# Get today's plan
plan = daily_plan[daily_plan['date'] == '2026-01-11']
# Show: 3 outlets, 2 priority
```

### During Visit (SD0002)
```python
# Get LIPB history
lipb = lipb_tracking[lipb_tracking['outlet_id'] == 'SD0002']
# avg_lipb = 1.3, target = 3, trend = Declining

# Get top SKUs
skus = sku_performance_by_outlet[sku_performance_by_outlet['outlet_id'] == 'SD0002']
# Top 3: Coca-Cola 500ml, Kinley Water, Sprite 500ml

# Get coaching tip
tip = coaching_tips[coaching_tips['category'] == 'Upselling']
```

### End of Day
```python
# Calculate stats
completed = daily_plan[daily_plan['completed'] == 'Yes']
adherence = len(completed) / len(plan) * 100
```

---

## Notes

- All data is **mock data** for POC purposes
- Focused on **one DSR: Nalin Perera**
- **No route planning data** (waiting for Google Maps API)
- Dates use **2026-01-11** as "today"
- Sales values in **Sri Lankan Rupees (LKR)**
- All Sinhala text is in **Sinhala Unicode**

---

**Created:** 2026-01-11
**For:** CCS POPS Sales Coaching Assistant POC
