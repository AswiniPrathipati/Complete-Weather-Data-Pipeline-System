# src/validators.py — Data Validation & Quality Assurance
# ==========================================================

import logging
from datetime import datetime

try:
    from config.config import VALIDATION_RULES
except ImportError:
    from config import VALIDATION_RULES

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates weather records against defined business rules."""

    RULES = VALIDATION_RULES

    def validate_record(self, record: dict) -> tuple:
        issues = []
        issues += self._check_required_fields(record)
        issues += self._check_temperature(record)
        issues += self._check_humidity(record)
        issues += self._check_pressure(record)
        issues += self._check_wind(record)
        issues += self._check_timestamp(record)
        is_valid = len(issues) == 0
        if not is_valid:
            logger.warning("Validation failed [%s]: %s", record.get('city', '?'), issues)
        return is_valid, issues

    def quality_report(self, records: list) -> dict:
        total  = len(records)
        passed = sum(1 for r in records if self.validate_record(r)[0])
        return {
            'total':         total,
            'passed':        passed,
            'failed':        total - passed,
            'pass_rate_pct': round(100 * passed / total, 2) if total else 0,
        }

    # ── Individual checks ────────────────────────────────

    def _check_required_fields(self, rec):
        return [f"Missing: {f}" for f in
                ['city', 'timestamp', 'temperature_c', 'humidity', 'pressure_hpa']
                if rec.get(f) is None]

    def _check_temperature(self, rec):
        t = rec.get('temperature_c')
        if t is None: return []
        issues = []
        if t < self.RULES['temperature_min']: issues.append(f"Temp {t} too low")
        if t > self.RULES['temperature_max']: issues.append(f"Temp {t} too high")
        return issues

    def _check_humidity(self, rec):
        h = rec.get('humidity')
        if h is None: return []
        return [f"Humidity {h} out of range [0,100]"] if not (0 <= h <= 100) else []

    def _check_pressure(self, rec):
        p = rec.get('pressure_hpa')
        if p is None: return []
        issues = []
        if p < self.RULES['pressure_min']: issues.append(f"Pressure {p} too low")
        if p > self.RULES['pressure_max']: issues.append(f"Pressure {p} too high")
        return issues

    def _check_wind(self, rec):
        w = rec.get('wind_speed_mps')
        if w is None: return []
        issues = []
        if w < 0:                            issues.append(f"Wind {w} is negative")
        if w > self.RULES['wind_speed_max']: issues.append(f"Wind {w} too high")
        return issues

    def _check_timestamp(self, rec):
        ts = rec.get('timestamp')
        if not ts: return []
        try:
            parsed = datetime.fromisoformat(str(ts)) if isinstance(ts, str) else ts
            if parsed.replace(tzinfo=None) > datetime.utcnow():
                return [f"Timestamp {ts} is in the future"]
        except ValueError:
            return [f"Invalid timestamp: {ts}"]
        return []
