# 🌦️ Weather Data Pipeline System

> **Advanced Real-Time ETL Pipeline with Monitoring, Alerts & Automated Reporting**

---

## 📖 Overview

A production-grade, end-to-end data engineering pipeline that:

- 📡 **Extracts** live weather data from OpenWeatherMap API for **15 Indian cities**
- 🔄 **Transforms** and validates records with quality assurance checks
- 💾 **Loads** clean data into a normalized **SQLite database** (4 tables)
- 🔔 **Alerts** on threshold breaches (high temp, low pressure, high wind, etc.)
- 📊 **Reports** via console dashboards and styled HTML reports
- 🏥 **Monitors** pipeline health with consecutive failure detection
- ⏰ **Schedules** automated runs every 60 minutes

---

## 🗂️ Project Structure

```
weather-pipeline/
├── README.md                        ← You are here
├── requirements.txt                 ← Python dependencies
│
├── config/
│   ├── config.py                    ← All settings (API, cities, thresholds)
│   └── logging_config.py            ← Centralized logging setup
│
├── src/
│   ├── api_client.py                ← OpenWeatherMap API client
│   ├── database.py                  ← DB connection + all CRUD operations
│   ├── etl_pipeline.py              ← Extract → Transform → Load → Alert
│   ├── validators.py                ← Data quality & validation rules
│   ├── reporter.py                  ← Dashboard + HTML report generator
│   ├── monitor.py                   ← Pipeline health monitoring
│   └── scheduler.py                 ← Automated job scheduling
│
├── database/
│   ├── schema.sql                   ← Full SQL schema (all 4 tables)
│   └── weather_data.db              ← SQLite database (auto-created on run)
│
├── tests/
│   ├── test_validators.py           ← Unit tests for DataValidator
│   ├── test_api_client.py           ← Unit tests for API parser
│   └── test_pipeline.py             ← Integration tests
│
├── docs/
│   ├── architecture.md              ← System architecture & design decisions
│   ├── api_reference.md             ← Module & function reference
│   └── deployment.md                ← Deployment & maintenance guide
│
├── scripts/
│   ├── run_pipeline.py              ← One-click pipeline runner
│   ├── reset_database.py            ← Reset DB to clean state
│   └── export_data.py               ← Export DB to CSV
│
├── logs/
│   ├── pipeline.log                 ← Sample ETL run logs
│   └── monitor.log                  ← Sample health check logs
│
└── reports/
    └── sample_report.html           ← Sample generated HTML report
```

---

## 🗄️ Database Schema (4 Normalized Tables)

| Table | Purpose |
|-------|---------|
| `cities` | Master list of tracked cities with coordinates |
| `weather_data` | All weather readings (temperature, humidity, pressure, wind) |
| `weather_alerts` | Threshold-triggered alerts with severity levels |
| `pipeline_logs` | ETL run history, durations, and status |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- OpenWeatherMap API key (free at https://openweathermap.org/api)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/weather-pipeline.git
cd weather-pipeline
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API key
```bash
# Option A — Environment variable (recommended)
export OPENWEATHER_API_KEY="your_api_key_here"

# Option B — Edit directly
# Open config/config.py and set API_KEY = "your_api_key_here"
```

### 5. Initialise the database
```bash
python scripts/run_pipeline.py setup
```

### 6. Test API connection
```bash
python scripts/run_pipeline.py test
```

---

## 🚀 Running the Pipeline

```bash
# Run ETL once
python scripts/run_pipeline.py run

# Start automated scheduler (runs every 60 min)
python scripts/run_pipeline.py schedule

# Print dashboard + save HTML report
python scripts/run_pipeline.py report

# Pipeline health check
python scripts/run_pipeline.py monitor

# Export data to CSV
python scripts/export_data.py
```

### Run in Google Colab
Open `Weather_Pipeline_Colab.ipynb` in Google Colab and run all cells.

---

## 📊 Sample Output

```
============================================================
       WEATHER DATA PIPELINE SYSTEM — DASHBOARD
============================================================
📊 System Status  : RUNNING
⏰ Report Time    : 2024-01-15 09:00:00
🗄️  Total Records  : 10,250
🏙️  Cities Tracked : 15
✅ Data Quality   : 98.5%
🔔 Open Alerts    : 2

🌤️  CURRENT WEATHER SNAPSHOT:
------------------------------------------------------------
  ☀️  Mumbai          28.5°C  💧65%  💨3.5 m/s  Clear Sky
  ☁️  Delhi           22.3°C  💧45%  💨4.1 m/s  Partly Cloudy
  🌧️  Bangalore       24.8°C  💧70%  💨2.2 m/s  Light Rain
  ☀️  Chennai         30.2°C  💧75%  💨5.0 m/s  Sunny

🚨 ACTIVE ALERTS:
------------------------------------------------------------
  🔴 [HIGH_TEMP]     Chennai: 30.2°C > 30°C threshold
  🟡 [HIGH_HUMIDITY] Kolkata: 86% > 85% threshold
```

---

## 🔔 Alert Thresholds

| Alert | Threshold | Severity |
|-------|-----------|----------|
| HIGH_TEMP | > 35°C | WARNING |
| LOW_TEMP | < 5°C | INFO |
| HIGH_HUMIDITY | > 85% | INFO |
| HIGH_WIND | > 15 m/s | WARNING |
| LOW_PRESSURE | < 990 hPa | WARNING |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | 2.31.0 | HTTP API client |
| `pandas` | 2.1.4 | Data analysis |
| `schedule` | 1.2.1 | Job scheduling |
| `python-dotenv` | 1.0.0 | Environment variables |
| `matplotlib` | 3.8.0 | Charts & visualizations |

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
# or
python -m unittest discover tests/
```

---

## 📋 Analysis Capabilities

1. **Hottest city** — Average temperature ranking across all cities
2. **Temperature trends** — Hourly/daily trends over configurable time windows
3. **Humidity correlation** — Humidity vs weather condition analysis
4. **Peak temperature hours** — By-hour averages per city
5. **Seasonal patterns** — Monthly aggregation queries

---

## 👨‍💻 Author

Weather Data Pipeline — Advanced Version  
Built as a complete data engineering project submission.
