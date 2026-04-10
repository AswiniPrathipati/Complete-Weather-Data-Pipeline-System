# tests/test_pipeline.py — Integration Tests
# ============================================

import unittest
import sqlite3
import tempfile
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabaseIntegration(unittest.TestCase):
    """Test database operations using an in-memory SQLite database."""

    def setUp(self):
        self.db_file = tempfile.mktemp(suffix='.db')
        # Patch DB_PATH for tests
        import config.config as cfg
        self._orig_path = cfg.DB_PATH
        cfg.DB_PATH = self.db_file

        from src.database import setup_database, insert_city, insert_weather_record, get_latest_weather
        self.setup_database      = setup_database
        self.insert_city         = insert_city
        self.insert_weather_record = insert_weather_record
        self.get_latest_weather  = get_latest_weather

        setup_database()

    def tearDown(self):
        import config.config as cfg
        cfg.DB_PATH = self._orig_path
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_database_created(self):
        self.assertTrue(os.path.exists(self.db_file))

    def test_insert_and_retrieve_city(self):
        cid = self.insert_city('TestCity', 'IN', 17.0, 81.0)
        self.assertIsNotNone(cid)
        self.assertIsInstance(cid, int)

    def test_duplicate_city_ignored(self):
        cid1 = self.insert_city('Uniq', 'IN', 10.0, 10.0)
        cid2 = self.insert_city('Uniq', 'IN', 10.0, 10.0)
        self.assertEqual(cid1, cid2)

    def test_insert_weather_record(self):
        cid = self.insert_city('WeatherCity', 'IN', 15.0, 75.0)
        record = {
            'city_id': cid, 'timestamp': '2024-01-15T08:00:00',
            'temperature_c': 28.5, 'feels_like_c': 30.0,
            'temp_min_c': 26.0, 'temp_max_c': 31.0,
            'humidity': 65, 'pressure_hpa': 1013.0,
            'wind_speed_mps': 3.5, 'wind_direction': 180,
            'visibility_m': 10000, 'cloudiness_pct': 20,
            'weather_condition': 'clear sky', 'weather_icon': '01d',
            'temp_label': 'Warm', 'is_valid': 1,
        }
        self.insert_weather_record(record)
        rows = self.get_latest_weather()
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]['temperature_c'], 28.5)

    def test_all_four_tables_exist(self):
        conn = sqlite3.connect(self.db_file)
        cur  = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}
        conn.close()
        expected = {'cities', 'weather_data', 'weather_alerts', 'pipeline_logs'}
        self.assertTrue(expected.issubset(tables), f"Missing tables: {expected - tables}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
