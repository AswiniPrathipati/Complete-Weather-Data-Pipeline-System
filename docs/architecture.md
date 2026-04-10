# 🏗️ System Architecture

## Overview

The Weather Data Pipeline follows a classic **ETL (Extract → Transform → Load)** architecture with an additional **Alert** and **Monitor** layer on top.

```
┌─────────────────────────────────────────────────────────┐
│                    SCHEDULER (scheduler.py)              │
│         Triggers ETL every 60 min | Report at 8AM       │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  ETL PIPELINE (etl_pipeline.py)          │
│                                                          │
│  ┌──────────┐  ┌─────────────┐  ┌──────┐  ┌─────────┐ │
│  │ EXTRACT  │→ │  TRANSFORM  │→ │ LOAD │→ │  ALERT  │ │
│  │api_client│  │ validators  │  │  DB  │  │threshold│ │
│  └──────────┘  └─────────────┘  └──────┘  └─────────┘ │
└──────────────────────────┬──────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ cities   │  │ weather  │  │ alerts   │
       │  table   │  │  data    │  │  table   │
       └──────────┘  └──────────┘  └──────────┘
                          │
                          ▼
              ┌────────────────────┐
              │  REPORTER          │
              │  Console Dashboard │
              │  HTML Reports      │
              └────────────────────┘
                          │
                          ▼
              ┌────────────────────┐
              │  MONITOR           │
              │  Health Checks     │
              │  Failure Detection │
              └────────────────────┘
```

---

## Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `config/config.py` | Single source of truth for all settings |
| `src/api_client.py` | HTTP calls to OpenWeatherMap with retry logic |
| `src/validators.py` | Business rule validation on incoming records |
| `src/database.py` | All SQLite CRUD operations |
| `src/etl_pipeline.py` | Orchestrates the full Extract→Transform→Load→Alert flow |
| `src/reporter.py` | Generates console dashboard and HTML reports |
| `src/monitor.py` | Checks pipeline health and writes monitor.log |
| `src/scheduler.py` | Time-based job scheduling using the `schedule` library |

---

## Data Flow

1. **Scheduler** triggers the ETL pipeline every 60 minutes
2. **ETL Pipeline** calls the API client for each of the 15 cities
3. **API Client** fetches live data from OpenWeatherMap using lat/lon coordinates
4. **Transformer** enriches records (adds `temp_label`) and runs validation
5. **Validator** checks all business rules; marks invalid records with `is_valid=0`
6. **Database** stores all records (valid + invalid) for auditability
7. **Alert Engine** checks 5 threshold rules and inserts alerts if triggered
8. **Reporter** reads the database and generates dashboard output
9. **Monitor** reads `pipeline_logs` to assess system health

---

## Design Decisions

- **SQLite** chosen for portability and zero-infrastructure setup
- **Coordinate-based API calls** used instead of city names for higher accuracy
- **is_valid flag** preserves invalid records rather than discarding them — enables data quality auditing
- **Retry logic** with exponential back-off protects against transient API failures
- **Rotating log files** prevent unbounded disk usage in long-running deployments
