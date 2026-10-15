# WL Predictor — Railway Waitlist Confirmation Prediction & Daily Analytics System
https://preeminent-chebakia-1c261a.netlify.app/
> **A beginner-friendly, statistical web application to estimate railway waitlist confirmation probabilities, track daily waiting-list drops on visual timelines, and explore network-wide cancellation trends.**

---

## 📌 Problem Statement
Passengers booking railway tickets frequently encounter a **Waitlisted (WL)** status instead of a confirmed berth. Travelers are left wondering:
- *Will this ticket confirm before departure?*
- *Is the waitlist clearing fast enough?*
- *Should I book an alternative train or Tatkal?*

**WL Predictor** answers these questions by combining **queue position**, **historical daily waitlist drops**, **cancellation velocity**, **travel class quotas**, and **days remaining** into an explainable, transparent probability score with full daily movement tracking.

---

## 🎯 Key Features & Pages

1. **Home Page (`/`)**
   - High-definition hero section featuring a scenic train at sunrise.
   - One-line intuitive explanation and primary *"Check My Ticket"* CTA button.
   - Three structured step cards: **1. Enter details &rarr; 2. See chance &rarr; 3. Track daily**.
   - Live system statistics strip (tickets checked, confirmed berths, RAC clearances, avg daily cancellations).

2. **Predict Page (`/predict`)**
   - Form capturing:
     - **Train Number** (e.g. 12951 Rajdhani, 12626 Kerala Express)
     - **Journey Date**
     - **Travel Class** (SL, 3A, 2A, 1A, CC)
     - **Booking Quota** (General, Tatkal, Ladies, Senior Citizen)
     - **Current Waiting-List Number**
     - **Days Remaining**
   - Platform side banner with railway travel tips.
   - **Result Card**:
     - Large percentage display (e.g. `84%`).
     - Category badge: **High (70%+)**, **Medium (40-69%)**, **Low (&lt;40%)**.
     - Colored, animated progress bar (Green, Amber, Red).
     - Plain-English one-line explanation.
     - **Formula Breakdown**: transparent point-by-point view of baseline score, position points, time window points, clearance velocity, class/quota offsets, and cancellation adjustments.
     - Direct button to track daily movement for this ticket.

3. **WL Movement Tracker (`/movement`)**
   - Select and switch between any tracked ticket.
   - Visual progression timeline: e.g. **WL 35 &rarr; WL 28 &rarr; WL 21 &rarr; WL 15**.
   - Metric cards: Starting WL, Latest WL, Total Drop, and Daily Clearance Velocity.
   - **Interactive Chart.js Line Chart** showing `WL Number vs. Date`.
   - Quick form to log today's new WL status update.
   - Complete tabular history with drop-rate indicators.

4. **Analytics Dashboard (`/analytics`)**
   - Station signals header banner at twilight.
   - **5 Summary Cards**: Total Tickets Checked, Confirmed (CNF), RAC Clearances, Still Waiting, and Average Daily Cancellations.
   - **Chart.js Bar Chart**: Daily Cancellations across tracked train dates.
   - **Chart.js Doughnut Chart**: Final ticket outcomes distribution (Confirmed vs RAC vs Waiting).
   - Recent predictions log table with real-time probability bars and direct links to movement tracking.

5. **About Page (`/about`)**
   - Panoramic train interior photography.
   - Explanation of the 6 mathematical scoring pillars.
   - Category thresholds and definitions.
   - FAQs (RAC berths, Tatkal cancellation restrictions, chart preparation 4 hours before departure).
   - Prominent system disclaimer.

---

## 🧮 Prediction Logic & Scoring Model

The algorithm starts from a balanced neutral anchor and applies transparent adjustments:

| Factor | Condition / Input | Points Adjustment | Rationale |
|---|---|---|---|
| **Base Score** | Default anchor | **+50%** | Median statistical baseline |
| **WL Position** | WL 1 - 5<br>WL 6 - 15<br>WL 16 - 30<br>WL 31 - 50<br>WL 51 - 90<br>WL &gt; 90 | **+25%**<br>**+15%**<br>**+5%**<br>**-8%**<br>**-20%**<br>**-32%** | Lower waitlists require fewer seat cancellations to clear. |
| **Days Left** | &gt; 15 days<br>7 - 15 days<br>3 - 6 days<br>2 days<br>&le; 1 day | **+15%**<br>**+10%**<br>**+4%**<br>**-4%**<br>**-18%** | More days provide more time for passenger cancellations; &le;1 day means chart preparation is imminent. |
| **Daily Drop Velocity** | &ge; 6.0 drops/day<br>&ge; 3.0 drops/day<br>&ge; 1.0 drop/day<br>&le; 0 | **+16%**<br>**+10%**<br>**+4%**<br>**-12%** | Computed from stored `wl_history`. Rapid clearing queues confirm faster. |
| **Class Adjustment** | Sleeper (SL)<br>3A<br>2A<br>1A<br>CC | **+10%**<br>**+5%**<br>**-5%**<br>**-14%**<br>**+2%** | SL has the largest number of coaches (10-14); 1A has minimal coaches and berths. |
| **Quota Adjustment** | General (GN)<br>Tatkal (TQ)<br>Ladies / Senior | **+5%**<br>**-16%**<br>**+2%** | Tatkal tickets have zero refund upon cancellation, so passengers almost never cancel confirmed Tatkal berths. |
| **Cancellations** | Route cancellation average | **-2% to +10%** | Higher historical cancellations free up more vacant berths. |

> **Final Score:** Clamped strictly between **1%** and **99%**.
> - **High:** 70%+ (Signal Green)
> - **Medium:** 40% - 69% (Signal Amber)
> - **Low:** Below 40% (Signal Red)

---

## 🗄️ Database Architecture (SQLite)

The SQLite database (`railway_wl.db`) automatically initializes on first run with sample data:

1. `tickets` — Stores predicted tickets with train number, journey date, class, quota, WL position, days left, probability score, and category.
2. `wl_history` — Stores timestamped daily status updates linked by `ticket_id`.
3. `cancellations` — Stores route-specific daily cancellation counts.
4. `outcomes` — Pre-filled with **35+ realistic historical journey outcomes** across popular Indian Railways trains (Mumbai Rajdhani 12951, Howrah Rajdhani 12301, Kerala Express 12626, Sealdah Duronto 12259, Lucknow Shatabdi 12004, Punjab Mail 12138).

---

## 📁 File Structure

```
dsa-mini-project/
├── app.py                  # Flask web application and routing
├── database.py             # SQLite database layer, schema & sample seeding
├── predictor.py            # Transparent prediction logic engine
├── requirements.txt        # Python dependencies (Flask)
├── README.md               # Complete documentation and setup guide
├── static/
│   ├── css/
│   │   └── style.css       # Custom vanilla CSS design system & railway theme
│   ├── js/
│   │   └── charts.js       # Chart.js scripts (line, bar, doughnut charts)
│   └── images/             # Railway photography assets
│       ├── hero_train.jpg         # Train on tracks at sunrise
│       ├── predict_platform.jpg   # Railway platform side banner
│       ├── analytics_signal.jpg   # Twilight railway signals & hub
│       └── about_interior.jpg     # Train interior passenger cabin
└── templates/
    ├── base.html           # Base layout, navbar, rail-track divider, footer
    ├── index.html          # Home page with hero & 3 step cards
    ├── predict.html        # Prediction form, platform banner & result card
    ├── movement.html       # Daily status tracker, timeline & line chart
    ├── analytics.html      # KPI cards, bar chart, outcomes doughnut & table
    └── about.html          # Methodology, 6 pillars, FAQs & disclaimer
```

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Python 3.8 or newer installed on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Application
```bash
python app.py
```

### 4. Open in Your Web Browser
Visit:
```
http://127.0.0.1:5000/
```

---

## ⚠️ Important Disclaimer
> **This is an estimate, not a guarantee.**
> All confirmation probabilities and category classifications provided by **WL Predictor** are statistical estimates derived from historical queues, passenger cancellation habits, and booking trends. Final berth allocations and chart preparations are solely determined by railway reservation systems.
