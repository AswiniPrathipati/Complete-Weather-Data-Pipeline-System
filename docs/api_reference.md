# 📚 API Reference

## config/config.py

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_KEY` | str | env var | OpenWeatherMap API key |
| `CITIES` | list[dict] | 15 cities | Cities to track |
| `DB_PATH` | str | `database/weather_data.db` | SQLite file path |
| `ALERT_THRESHOLDS` | dict | see below | Threshold values for alerts |
| `VALIDATION_RULES` | dict | see below | Min/max bounds for validation |
| `SCHEDULE_INTERVAL_MINUTES` | int | 60 | ETL run frequency |

---

## src/api_client.py — `WeatherAPIClient`

### `fetch_weather_by_coords(lat, lon, city_name) → dict | None`
Fetches current weather using GPS coordinates. Returns a normalized dict or None on failure.

### `fetch_current_weather(city_name, country) → dict | None`
Fetches current weather using city name string.

### `fetch_forecast(city_name, country) → list[dict]`
Returns 5-day / 3-hour forecast as a list of records.

### `test_connection() → bool`
Pings the API using London,GB. Returns True if successful.

**Returned record keys:**
`city, country, timestamp, temperature_c, feels_like_c, temp_min_c, temp_max_c,
humidity, pressure_hpa, wind_speed_mps, wind_direction, visibility_m,
cloudiness_pct, weather_condition, weather_icon`

---

## src/validators.py — `DataValidator`

### `validate_record(record: dict) → (bool, list[str])`
Validates a single weather record. Returns `(True, [])` if valid, or `(False, [issues])`.

**Checks performed:**
- Required fields present
- Temperature in [-50, 60] °C
- Humidity in [0, 100] %
- Pressure in [870, 1084] hPa
- Wind speed ≥ 0 and ≤ 90 m/s
- Timestamp is not in the future

### `quality_report(records: list) → dict`
Runs validation on a batch. Returns `{total, passed, failed, pass_rate_pct}`.

---

## src/database.py

### `setup_database()`
Creates all 4 tables and indexes if they don't exist.

### `insert_city(city_name, country, latitude, longitude) → int`
Inserts a city (or ignores if duplicate). Returns `city_id`.

### `insert_weather_record(record: dict)`
Inserts one weather reading into `weather_data`.

### `insert_alert(city_id, alert_type, message, metric_value, threshold, severity)`
Logs a triggered alert into `weather_alerts`.

### `log_pipeline_run(...)`
Records an ETL run summary into `pipeline_logs`.

### `get_latest_weather(city_name=None) → list[dict]`
Returns the most recent valid record per city (or for one city).

### `get_weather_history(city_name, days=30) → list[dict]`
Returns all valid records for a city over the last N days.

### `get_database_stats() → dict`
Returns `{total_records, active_cities, open_alerts, last_record_time, data_quality_pct}`.

---

## src/etl_pipeline.py — `WeatherETLPipeline`

### `run() → dict`
Executes the full pipeline. Returns a summary dict:
```python
{
  'status':            'SUCCESS' | 'FAILED',
  'cities_processed':  int,
  'records_inserted':  int,
  'records_failed':    int,
  'alerts_triggered':  int,
  'duration_seconds':  float,
  'error_message':     str | None,
}
```

---

## src/reporter.py — `WeatherReporter`

### `print_dashboard()`
Prints the live weather dashboard to stdout.

### `generate_html_report() → str`
Generates and saves a styled HTML report. Returns the file path.

### `city_avg_temperature(days=30) → list[dict]`
Returns average, min, max temperature per city over N days.

### `recent_alerts(limit=20) → list[dict]`
Returns the most recent unresolved alerts.

---

## src/monitor.py — `PipelineMonitor`

### `run_health_check() → dict`
Runs all health checks and returns:
```python
{
  'timestamp':           str,
  'overall_status':      'HEALTHY' | 'WARNING' | 'CRITICAL',
  'checks': {
    'database_accessible':  bool,
    'data_freshness':       dict,
    'recent_run_status':    dict,
    'consecutive_failures': int,
    'disk_space_mb':        float,
  }
}
```

### `print_status()`
Prints a formatted health report to stdout.

---

## src/scheduler.py

### `start_scheduler()`
Starts the blocking scheduler loop. Jobs:
- ETL pipeline: every `SCHEDULE_INTERVAL_MINUTES` minutes
- Daily report: every day at `REPORT_SCHEDULE_HOUR:00`
- Health check: every `HEALTH_CHECK_INTERVAL` seconds

Handles `SIGINT` / `SIGTERM` for graceful shutdown.
