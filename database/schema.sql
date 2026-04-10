-- =============================================================
-- Weather Data Pipeline — Full Database Schema
-- SQLite | 4 normalized tables
-- =============================================================

PRAGMA foreign_keys = ON;

-- -------------------------------------------------------------
-- Table 1: cities
-- Master list of tracked cities with GPS coordinates
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cities (
    city_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name  TEXT    NOT NULL,
    country    TEXT    NOT NULL DEFAULT 'IN',
    latitude   REAL    NOT NULL,
    longitude  REAL    NOT NULL,
    is_active  INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_name, country)
);

-- -------------------------------------------------------------
-- Table 2: weather_data
-- All weather readings fetched from the API
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather_data (
    record_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id           INTEGER NOT NULL,
    timestamp         TIMESTAMP NOT NULL,
    temperature_c     REAL,
    feels_like_c      REAL,
    temp_min_c        REAL,
    temp_max_c        REAL,
    humidity          INTEGER,
    pressure_hpa      REAL,
    wind_speed_mps    REAL,
    wind_direction    INTEGER,
    visibility_m      INTEGER,
    cloudiness_pct    INTEGER,
    weather_condition TEXT,
    weather_icon      TEXT,
    temp_label        TEXT,           -- e.g. Hot / Warm / Cool / Cold
    is_valid          INTEGER NOT NULL DEFAULT 1,  -- data quality flag
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- -------------------------------------------------------------
-- Table 3: weather_alerts
-- Threshold-triggered alerts with severity classification
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather_alerts (
    alert_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id       INTEGER NOT NULL,
    alert_type    TEXT    NOT NULL,   -- HIGH_TEMP | LOW_TEMP | HIGH_HUMIDITY | HIGH_WIND | LOW_PRESSURE
    alert_message TEXT    NOT NULL,
    metric_value  REAL,
    threshold     REAL,
    severity      TEXT DEFAULT 'WARNING',  -- WARNING | INFO
    is_resolved   INTEGER DEFAULT 0,
    triggered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at   TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- -------------------------------------------------------------
-- Table 4: pipeline_logs
-- ETL run history — used for health monitoring
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pipeline_logs (
    log_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status           TEXT NOT NULL,   -- SUCCESS | FAILED
    cities_processed INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_failed   INTEGER DEFAULT 0,
    alerts_triggered INTEGER DEFAULT 0,
    duration_seconds REAL,
    error_message    TEXT
);

-- -------------------------------------------------------------
-- Indexes for query performance
-- -------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_data(city_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_city       ON weather_alerts(city_id, triggered_at);
CREATE INDEX IF NOT EXISTS idx_pipeline_status   ON pipeline_logs(status, run_timestamp);

-- =============================================================
-- Sample analytical queries
-- =============================================================

-- Q1: City with highest average temperature (last 30 days)
-- SELECT c.city_name, ROUND(AVG(w.temperature_c), 2) AS avg_temp
-- FROM weather_data w JOIN cities c ON w.city_id = c.city_id
-- WHERE w.is_valid = 1 AND w.timestamp >= datetime('now', '-30 days')
-- GROUP BY c.city_name ORDER BY avg_temp DESC;

-- Q2: Temperature trend for Mumbai (last 7 days)
-- SELECT strftime('%Y-%m-%d %H:00', timestamp) AS hour,
--        ROUND(AVG(temperature_c), 2) AS avg_temp
-- FROM weather_data w JOIN cities c ON w.city_id = c.city_id
-- WHERE c.city_name = 'Mumbai' AND w.is_valid = 1
--   AND timestamp >= datetime('now', '-7 days')
-- GROUP BY hour ORDER BY hour;

-- Q3: Humidity vs weather condition
-- SELECT weather_condition, ROUND(AVG(humidity), 1) AS avg_humidity, COUNT(*) AS count
-- FROM weather_data WHERE is_valid = 1 AND weather_condition IS NOT NULL
-- GROUP BY weather_condition ORDER BY avg_humidity DESC;

-- Q4: Active alerts
-- SELECT a.alert_type, c.city_name, a.alert_message, a.triggered_at
-- FROM weather_alerts a JOIN cities c ON a.city_id = c.city_id
-- WHERE a.is_resolved = 0 ORDER BY a.triggered_at DESC;

-- Q5: Pipeline run summary
-- SELECT status, COUNT(*) AS runs, ROUND(AVG(duration_seconds), 2) AS avg_duration
-- FROM pipeline_logs GROUP BY status;
