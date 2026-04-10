# tests/test_validators.py — Unit Tests: DataValidator
# ========================================================

import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.validators import DataValidator


class TestDataValidator(unittest.TestCase):

    def setUp(self):
        self.v = DataValidator()
        self.good = {
            'city': 'Mumbai', 'timestamp': '2024-01-15T08:00:00',
            'temperature_c': 28.5, 'humidity': 65,
            'pressure_hpa': 1013.0, 'wind_speed_mps': 3.5
        }

    def test_valid_record_passes(self):
        ok, issues = self.v.validate_record(self.good)
        self.assertTrue(ok, f"Expected valid but got: {issues}")

    def test_missing_temperature(self):
        rec = dict(self.good); del rec['temperature_c']
        ok, issues = self.v.validate_record(rec)
        self.assertFalse(ok)
        self.assertTrue(any('temperature_c' in i for i in issues))

    def test_missing_city(self):
        rec = dict(self.good); del rec['city']
        ok, _ = self.v.validate_record(rec)
        self.assertFalse(ok)

    def test_temperature_above_max(self):
        ok, _ = self.v.validate_record({**self.good, 'temperature_c': 70.0})
        self.assertFalse(ok)

    def test_temperature_below_min(self):
        ok, _ = self.v.validate_record({**self.good, 'temperature_c': -60.0})
        self.assertFalse(ok)

    def test_humidity_over_100(self):
        ok, _ = self.v.validate_record({**self.good, 'humidity': 110})
        self.assertFalse(ok)

    def test_humidity_negative(self):
        ok, _ = self.v.validate_record({**self.good, 'humidity': -5})
        self.assertFalse(ok)

    def test_pressure_too_low(self):
        ok, _ = self.v.validate_record({**self.good, 'pressure_hpa': 800.0})
        self.assertFalse(ok)

    def test_negative_wind(self):
        ok, _ = self.v.validate_record({**self.good, 'wind_speed_mps': -2.0})
        self.assertFalse(ok)

    def test_boundary_temperature_valid(self):
        ok, _ = self.v.validate_record({**self.good, 'temperature_c': 60.0})
        self.assertTrue(ok)

    def test_quality_report_mixed_batch(self):
        records = [
            self.good,
            {**self.good, 'temperature_c': 80.0},   # invalid
            {**self.good, 'humidity': -10},           # invalid
        ]
        qr = self.v.quality_report(records)
        self.assertEqual(qr['total'],  3)
        self.assertEqual(qr['passed'], 1)
        self.assertEqual(qr['failed'], 2)
        self.assertAlmostEqual(qr['pass_rate_pct'], 33.33, places=1)

    def test_quality_report_all_valid(self):
        records = [self.good, {**self.good, 'city': 'Delhi'}]
        qr = self.v.quality_report(records)
        self.assertEqual(qr['pass_rate_pct'], 100.0)

    def test_quality_report_empty(self):
        qr = self.v.quality_report([])
        self.assertEqual(qr['total'], 0)
        self.assertEqual(qr['pass_rate_pct'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
