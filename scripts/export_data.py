#!/usr/bin/env python3
# scripts/export_data.py — Export weather data to CSV
# =====================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.logging_config  # noqa
import pandas as pd
from datetime import datetime
from src.database import get_connection
from config.config import REPORTS_DIR

def export():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    conn = get_connection()

    df = pd.read_sql_query('''
        SELECT c.city_name, c.country, w.timestamp,
               w.temperature_c, w.feels_like_c, w.humidity,
               w.pressure_hpa, w.wind_speed_mps, w.wind_direction,
               w.cloudiness_pct, w.weather_condition, w.temp_label, w.is_valid
        FROM weather_data w
        JOIN cities c ON w.city_id = c.city_id
        ORDER BY w.timestamp DESC
    ''', conn)
    conn.close()

    fname = os.path.join(REPORTS_DIR, f"weather_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(fname, index=False)
    print(f"✅ Exported {len(df):,} records → {fname}")

if __name__ == "__main__":
    export()
