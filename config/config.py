# config/config.py — All Configuration Settings
# ================================================

import os

# ── API ────────────────────────────────────────────────────
API_KEY      = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL     = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
API_TIMEOUT  = 10
MAX_RETRIES  = 3
RETRY_DELAY  = 5

# ── Cities ─────────────────────────────────────────────────
CITIES = [
    {"name": "Mumbai",     "country": "IN", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi",      "country": "IN", "lat": 28.6139, "lon": 77.2090},
    {"name": "Bangalore",  "country": "IN", "lat": 12.9716, "lon": 77.5946},
    {"name": "Chennai",    "country": "IN", "lat": 13.0827, "lon": 80.2707},
    {"name": "Hyderabad",  "country": "IN", "lat": 17.3850, "lon": 78.4867},
    {"name": "Kolkata",    "country": "IN", "lat": 22.5726, "lon": 88.3639},
    {"name": "Vijayawada", "country": "IN", "lat": 16.5062, "lon": 80.6480},
    {"name": "Pune",       "country": "IN", "lat": 18.5204, "lon": 73.8567},
    {"name": "Ahmedabad",  "country": "IN", "lat": 23.0225, "lon": 72.5714},
    {"name": "Jaipur",     "country": "IN", "lat": 26.9124, "lon": 75.7873},
    {"name": "Lucknow",    "country": "IN", "lat": 26.8467, "lon": 80.9462},
    {"name": "Surat",      "country": "IN", "lat": 21.1702, "lon": 72.8311},
    {"name": "Nagpur",     "country": "IN", "lat": 21.1458, "lon": 79.0882},
    {"name": "Bhopal",     "country": "IN", "lat": 23.2599, "lon": 77.4126},
    {"name": "Patna",      "country": "IN", "lat": 25.5941, "lon": 85.1376},
]

# ── Database ───────────────────────────────────────────────
DB_PATH        = "database/weather_data.db"
DB_BACKUP_DIR  = "database/backups"

# ── Scheduler ──────────────────────────────────────────────
SCHEDULE_INTERVAL_MINUTES = 60
REPORT_SCHEDULE_HOUR      = 8
HEALTH_CHECK_INTERVAL     = 300

# ── Alert Thresholds ───────────────────────────────────────
ALERT_THRESHOLDS = {
    "high_temp":     35.0,
    "low_temp":       5.0,
    "high_humidity": 85,
    "high_wind":     15.0,
    "low_pressure":  990.0,
}

# ── Validation Rules ───────────────────────────────────────
VALIDATION_RULES = {
    "temperature_min": -50.0, "temperature_max":  60.0,
    "humidity_min":      0,   "humidity_max":    100,
    "pressure_min":    870.0, "pressure_max":   1084.0,
    "wind_speed_min":    0.0, "wind_speed_max":   90.0,
}

# ── Logging ────────────────────────────────────────────────
LOG_DIR          = "logs"
LOG_FILE         = "logs/pipeline.log"
LOG_LEVEL        = "INFO"
LOG_MAX_BYTES    = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 5

# ── Reports ────────────────────────────────────────────────
REPORTS_DIR           = "reports"
REPORT_RETENTION_DAYS = 30

# ── Monitoring ─────────────────────────────────────────────
MONITOR_LOG              = "logs/monitor.log"
MAX_CONSECUTIVE_FAILURES = 3
