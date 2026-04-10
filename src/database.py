# src/database.py — Database Connection & All CRUD Operations
# =============================================================

import sqlite3
import logging
import os

try:
    from config.config import DB_PATH
except ImportError:
    from config import DB_PATH

logger = logging.getLogger(__name__)


def get_connection():
    """Return a SQLite connection with foreign keys enabled."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """Create all 4 tables and indexes if they don't exist."""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS cities (
        city_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        city_name  TEXT    NOT NULL,
        country    TEXT    NOT NULL DEFAULT 'IN',
        latitude   REAL    NOT NULL,
        longitude  REAL    NOT NULL,
        is_active  INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(city_name, country)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS weather_data (
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
        temp_label        TEXT,
        is_valid          INTEGER NOT NULL DEFAULT 1,
        created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (city_id) REFERENCES cities(city_id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS weather_alerts (
        alert_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id       INTEGER NOT NULL,
        alert_type    TEXT    NOT NULL,
        alert_message TEXT    NOT NULL,
        metric_value  REAL,
        threshold     REAL,
        severity      TEXT    DEFAULT 'WARNING',
        is_resolved   INTEGER DEFAULT 0,
        triggered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at   TIMESTAMP,
        FOREIGN KEY (city_id) REFERENCES cities(city_id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS pipeline_logs (
        log_id           INTEGER PRIMARY KEY AUTOINCREMENT,
        run_timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status           TEXT NOT NULL,
        cities_processed INTEGER DEFAULT 0,
        records_inserted INTEGER DEFAULT 0,
        records_failed   INTEGER DEFAULT 0,
        alerts_triggered INTEGER DEFAULT 0,
        duration_seconds REAL,
        error_message    TEXT
    )''')

    cur.execute('CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_data(city_id, timestamp)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_alerts_city ON weather_alerts(city_id, triggered_at)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_pipeline_status ON pipeline_logs(status, run_timestamp)')

    conn.commit()
    conn.close()
    logger.info("Database ready: %s", DB_PATH)


def insert_city(city_name, country, latitude, longitude):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO cities (city_name,country,latitude,longitude) VALUES (?,?,?,?)',
                (city_name, country, latitude, longitude))
    conn.commit()
    cur.execute('SELECT city_id FROM cities WHERE city_name=? AND country=?', (city_name, country))
    row = cur.fetchone()
    conn.close()
    return row['city_id'] if row else None


def insert_weather_record(rec: dict):
    conn = get_connection()
    conn.execute('''INSERT INTO weather_data (
        city_id,timestamp,temperature_c,feels_like_c,temp_min_c,temp_max_c,
        humidity,pressure_hpa,wind_speed_mps,wind_direction,
        visibility_m,cloudiness_pct,weather_condition,weather_icon,temp_label,is_valid
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
    (rec.get('city_id'), rec.get('timestamp'), rec.get('temperature_c'),
     rec.get('feels_like_c'), rec.get('temp_min_c'), rec.get('temp_max_c'),
     rec.get('humidity'), rec.get('pressure_hpa'), rec.get('wind_speed_mps'),
     rec.get('wind_direction'), rec.get('visibility_m'), rec.get('cloudiness_pct'),
     rec.get('weather_condition'), rec.get('weather_icon'),
     rec.get('temp_label'), rec.get('is_valid', 1)))
    conn.commit()
    conn.close()


def insert_alert(city_id, alert_type, message, metric_value, threshold, severity='WARNING'):
    conn = get_connection()
    conn.execute('INSERT INTO weather_alerts (city_id,alert_type,alert_message,metric_value,threshold,severity) VALUES (?,?,?,?,?,?)',
                 (city_id, alert_type, message, metric_value, threshold, severity))
    conn.commit()
    conn.close()


def log_pipeline_run(status, cities_processed, records_inserted,
                     records_failed, alerts_triggered, duration_seconds, error_message=None):
    conn = get_connection()
    conn.execute('''INSERT INTO pipeline_logs
        (status,cities_processed,records_inserted,records_failed,alerts_triggered,duration_seconds,error_message)
        VALUES (?,?,?,?,?,?,?)''',
        (status, cities_processed, records_inserted, records_failed,
         alerts_triggered, duration_seconds, error_message))
    conn.commit()
    conn.close()


def get_latest_weather(city_name=None):
    conn = get_connection()
    cur  = conn.cursor()
    if city_name:
        cur.execute('''SELECT w.*,c.city_name,c.country FROM weather_data w
            JOIN cities c ON w.city_id=c.city_id
            WHERE c.city_name=? AND w.is_valid=1 ORDER BY w.timestamp DESC LIMIT 1''', (city_name,))
    else:
        cur.execute('''SELECT w.*,c.city_name,c.country FROM weather_data w
            JOIN cities c ON w.city_id=c.city_id WHERE w.is_valid=1
            AND w.timestamp=(SELECT MAX(w2.timestamp) FROM weather_data w2
                WHERE w2.city_id=w.city_id AND w2.is_valid=1)
            ORDER BY c.city_name''')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_weather_history(city_name, days=30):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('''SELECT w.*,c.city_name FROM weather_data w
        JOIN cities c ON w.city_id=c.city_id
        WHERE c.city_name=? AND w.is_valid=1
          AND w.timestamp>=datetime('now',? || ' days')
        ORDER BY w.timestamp ASC''', (city_name, f'-{days}'))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_database_stats():
    conn = get_connection()
    cur  = conn.cursor()
    stats = {}
    cur.execute("SELECT COUNT(*) AS c FROM weather_data WHERE is_valid=1")
    stats['total_records'] = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM cities WHERE is_active=1")
    stats['active_cities'] = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM weather_alerts WHERE is_resolved=0")
    stats['open_alerts'] = cur.fetchone()['c']
    cur.execute("SELECT MAX(timestamp) AS ts FROM weather_data")
    stats['last_record_time'] = cur.fetchone()['ts']
    cur.execute("SELECT ROUND(100.0*SUM(is_valid)/NULLIF(COUNT(*),0),2) AS p FROM weather_data")
    stats['data_quality_pct'] = cur.fetchone()['p']
    conn.close()
    return stats
