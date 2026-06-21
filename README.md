# 🌍 Ecosphere — Carbon Footprint Awareness Platform

[![Python Version](https://img.shields.io/badge/python-3.12%2B-emerald.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/database-SQLite-blue.svg)](https://www.sqlite.org/)
[![ASGI Framework](https://img.shields.io/badge/backend-Starlette-blueviolet.svg)](https://www.starlette.io/)
[![UI Deployment](https://img.shields.io/badge/frontend-Vanilla%20CSS%20%7C%20Streamlit-orange.svg)](#how-to-run)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)

Ecosphere is a full-stack, production-grade carbon footprint estimation, analytics, and history-tracking platform. It is designed to empower users to measure, analyze, and simulate carbon footprint offsets. 

The project features a premium, dark-themed, emerald-green aesthetic and supports **Dual Deployment Modes**—a raw Vanilla HTML5/CSS/JS frontend powered by a Starlette API server, or an interactive, single-script Streamlit Data Application. Both variants interface with the same SQLite database ledger and calculation engines.

---

## 🌟 Key Features

1. **Step-by-Step Footprint Estimator**:
   * A stateful 4-step wizard evaluating:
     * **Transport**: Weekly car travel, engine fuel type (Petrol, Diesel, Hybrid, Electric), public transit commute, and annual short-haul/long-haul flights.
     * **Home Energy**: Monthly electricity consumption (kWh), primary heating fuel, and household size.
     * **Dietary Footprint**: Categorized selections (Meat Lover, Omnivore, Vegetarian, Vegan).
     * **Goods & Waste**: Annual shopping consumption habits and recycling compliance.
2. **Analytical Diagnostics Dashboard**:
   * **Real-time Calculations**: Instantaneous updates on input changes running at 60fps.
   * **Donut Category Share Chart**: Displays the precise share of emissions per category (Transport, Home, Diet, Goods) drawn using native browser SVG/Altair.
   * **Gauge limit Indicator**: Compares annual totals against the global sustainable target (**2.0 t CO2e**) and global average averages (**4.8 t CO2e**).
3. **Personalized Offsets Simulation**:
   * Actionable mitigation recommendations served by a backend heuristics rules engine based on the categories where you emit the most.
   * Checkable checklists allowing users to simulate adopting actions, dynamically recalculating the projected footprint in real-time.
4. **Local Database Ledger History**:
   * Logs history records locally in a fast SQLite database instance.
   * Formatted history table listing logs, carbon savings, and final totals.
   * Dynamic line trend graph plotting historical data to visualize reduction progress.

---

## 🗺️ Project Architecture

```
c:\Users\ashis\Videos\Captures\ecosphere/
├── .streamlit/
│   └── config.toml        # Streamlit dark green theme configurations
├── backend/
│   ├── __init__.py
│   ├── main.py            # Starlette ASGI API endpoints & static folder router
│   ├── database.py        # SQLite history database CRUD driver
│   ├── calculator.py      # Deterministic EPA / GHG conversion utility
│   ├── recommender.py     # Heuristic AI insights generator
│   └── tests.py           # Automated unit test suite
├── frontend/
│   ├── index.html         # Main dashboard & form wizard layout
│   ├── styles.css         # Glassmorphism visual dark-green styles stylesheet
│   └── app.js             # Client reactive controller, local calculations, & SVGs
├── app_streamlit.py       # Streamlit data application entrypoint
├── ecosphere.db           # Local SQLite database (created on startup)
├── run.ps1                # PowerShell helper startup menu launcher
└── README.md
```

---

## 💾 Database Schema

The historical ledger is committed locally to a SQLite database (`ecosphere.db`) using the following table schema:

```sql
CREATE TABLE IF NOT EXISTS footprint_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,                  -- ISO 8601 UTC date string
    car_distance REAL NOT NULL,               -- distance per week
    car_fuel_type TEXT NOT NULL,              -- Petrol, Diesel, Hybrid, Electric, None
    transit_distance REAL NOT NULL,           -- public transit per week
    short_flights INTEGER NOT NULL,           -- flights per year
    long_flights INTEGER NOT NULL,            -- flights per year
    electricity_usage REAL NOT NULL,          -- kWh per month
    heating_type TEXT NOT NULL,               -- Natural gas, Electric, Oil, Renewable/None
    household_size INTEGER NOT NULL,          -- occupants count
    diet_type TEXT NOT NULL,                  -- Vegan, Vegetarian, Average, Meat-heavy
    shopping_habits TEXT NOT NULL,            -- Low, Average, High
    recycling_habit TEXT NOT NULL,            -- Rarely, Sometimes, Always
    
    -- Calculated Emissions (stored in kg CO2e)
    transport_emissions REAL NOT NULL,
    home_emissions REAL NOT NULL,
    diet_emissions REAL NOT NULL,
    goods_emissions REAL NOT NULL,
    total_emissions REAL NOT NULL,
    simulated_savings REAL NOT NULL,
    simulated_total REAL NOT NULL
);
```

---

## 🧮 Calculations & Emission Factors

The calculation engine utilizes deterministic multipliers based on standard EPA and Greenhouse Gas Protocol documentation:

| Category | Input parameter | Conversion Factor (kg CO2e) |
| :--- | :--- | :--- |
| **Transport** | Car driving (km) | Petrol: `0.192`/km \| Diesel: `0.171`/km \| Hybrid: `0.106`/km \| EV: `0.053`/km |
| **Transport** | Public transit (km) | `0.082` / passenger-km |
| **Transport** | Short-haul flight | `220.0` / flight (< 1500 km) |
| **Transport** | Long-haul flight | `1050.0` / flight (>= 1500 km) |
| **Home Energy** | Grid Electricity (kWh) | Region-dependent: India `0.72` \| Global Avg `0.40` \| USA `0.36` \| EU `0.22` \| UK `0.18` \| Canada `0.08` |
| **Home Energy** | Heating Fuel (baseline) | Gas: `0.182`/kWh \| Oil: `0.265`/kWh \| Electric: `0.380`/kWh \| Solar/None: `0.030`/kWh |
| **Dietary** | Diet Type (annual) | Vegan: `1300` \| Vegetarian: `1600` \| Omnivore: `2400` \| Meat Lover: `3200` |
| **Goods & Waste** | Shopping (annual) | Low: `350` \| Average: `850` \| High: `1500` |
| **Goods & Waste** | Recycling (annual) | Always: `-140` (Credit) \| Sometimes: `0` \| Rarely: `+180` (Penalty) |

---

## 🛠️ Installation & Setup

### Prerequisites
Ensure you have **Python 3.12+** installed on your system.

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/ecosphere.git
   cd ecosphere
   ```
2. **Install Dependencies**:
   Install the required libraries:
   ```bash
   pip install starlette uvicorn streamlit pandas altair
   ```
3. **Verify the Test Suite**:
   Run the automated backend test suite to check calculation precision and SQLite DB functions:
   ```bash
   python -m backend.tests
   ```

---

## 🚀 How to Run

Launch the platform effortlessly in Windows using our PowerShell helper script:

1. Open PowerShell inside the folder:
   ```powershell
   .\run.ps1
   ```
2. Choose your deployment version:
   * **Option 1**: Starts the **Streamlit Dashboard** at **`http://127.0.0.1:8501`**.
   * **Option 2**: Launches the **Starlette Full-stack App** at **`http://127.0.0.1:8000`**.

---

## 📄 License
Distributed under the MIT License.
