# src/etl_pipeline.py — Main ETL Orchestrator
# ==============================================

import logging
import time
from datetime import datetime

try:
    from config.config import CITIES, ALERT_THRESHOLDS
    from src.database import setup_database, insert_city, insert_weather_record, insert_alert, log_pipeline_run
    from src.api_client import WeatherAPIClient
    from src.validators import DataValidator
except ImportError:
    from config import CITIES, ALERT_THRESHOLDS
    from database import setup_database, insert_city, insert_weather_record, insert_alert, log_pipeline_run
    from api_client import WeatherAPIClient
    from validators import DataValidator

logger = logging.getLogger(__name__)


class WeatherETLPipeline:
    """Orchestrates the full Extract → Transform → Load → Alert cycle."""

    def __init__(self):
        self.api_client      = WeatherAPIClient()
        self.validator       = DataValidator()
        self._city_id_cache  = {}

    def run(self) -> dict:
        start   = time.time()
        summary = {'status': 'SUCCESS', 'cities_processed': 0, 'records_inserted': 0,
                   'records_failed': 0, 'alerts_triggered': 0, 'error_message': None}
        logger.info("=" * 60)
        logger.info("ETL Pipeline started at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            setup_database()
            self._seed_cities()

            raw         = self._extract()
            summary['cities_processed'] = len(raw)

            transformed = self._transform(raw)
            qr          = self.validator.quality_report(transformed)
            logger.info("Quality: %d/%d passed (%.1f%%)", qr['passed'], qr['total'], qr['pass_rate_pct'])

            ins, fail   = self._load(transformed)
            summary['records_inserted'] = ins
            summary['records_failed']   = fail

            alerts      = self._check_alerts(transformed)
            summary['alerts_triggered'] = alerts

        except Exception as exc:
            summary['status']        = 'FAILED'
            summary['error_message'] = str(exc)
            logger.exception("Pipeline error: %s", exc)

        finally:
            dur = round(time.time() - start, 2)
            summary['duration_seconds'] = dur
            log_pipeline_run(**{k: summary[k] for k in [
                'status','cities_processed','records_inserted',
                'records_failed','alerts_triggered','error_message']},
                duration_seconds=dur)
            logger.info("Pipeline finished in %.2fs | %s", dur, summary['status'])

        return summary

    def _seed_cities(self):
        for city in CITIES:
            cid = insert_city(city['name'], city['country'], city['lat'], city['lon'])
            if cid:
                self._city_id_cache[city['name']] = cid

    def _extract(self) -> list:
        records = []
        for city in CITIES:
            data = self.api_client.fetch_weather_by_coords(city['lat'], city['lon'], city['name'])
            if data:
                records.append(data)
                logger.info("Extracted: %s", city['name'])
            else:
                logger.warning("Skipped: %s", city['name'])
        return records

    def _transform(self, raw: list) -> list:
        for rec in raw:
            rec['city_id'] = self._city_id_cache.get(rec['city'])
            valid, _       = self.validator.validate_record(rec)
            rec['is_valid'] = 1 if valid else 0
            t = rec.get('temperature_c', 0)
            rec['temp_label'] = ('Extreme Heat' if t>=40 else 'Very Hot' if t>=35
                                 else 'Hot' if t>=30 else 'Warm' if t>=20
                                 else 'Cool' if t>=10 else 'Cold')
        return raw

    def _load(self, records: list) -> tuple:
        ins = fail = 0
        for rec in records:
            try:
                insert_weather_record(rec)
                ins += 1
            except Exception as e:
                fail += 1
                logger.error("Insert failed [%s]: %s", rec.get('city'), e)
        return ins, fail

    def _check_alerts(self, records: list) -> int:
        thr = ALERT_THRESHOLDS
        count = 0
        for rec in records:
            if not rec.get('is_valid'):
                continue
            cid, city = rec.get('city_id'), rec.get('city', '?')
            checks = [
                ('HIGH_TEMP',     rec.get('temperature_c'),  thr['high_temp'],
                 lambda v,t: v is not None and v > t, 'WARNING'),
                ('LOW_TEMP',      rec.get('temperature_c'),  thr['low_temp'],
                 lambda v,t: v is not None and v < t, 'INFO'),
                ('HIGH_HUMIDITY', rec.get('humidity'),        thr['high_humidity'],
                 lambda v,t: v is not None and v > t, 'INFO'),
                ('HIGH_WIND',     rec.get('wind_speed_mps'), thr['high_wind'],
                 lambda v,t: v is not None and v > t, 'WARNING'),
                ('LOW_PRESSURE',  rec.get('pressure_hpa'),   thr['low_pressure'],
                 lambda v,t: v is not None and v < t, 'WARNING'),
            ]
            for atype, val, threshold, cond, sev in checks:
                if cond(val, threshold):
                    msg = f"{city}: {atype} — {val} (threshold: {threshold})"
                    insert_alert(cid, atype, msg, val, threshold, sev)
                    logger.warning("ALERT [%s] %s", sev, msg)
                    count += 1
        return count
