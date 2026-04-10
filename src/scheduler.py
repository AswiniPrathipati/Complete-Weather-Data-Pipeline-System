# src/scheduler.py — Automated Job Scheduler
# =============================================

import logging
import time
import signal
import sys

import schedule

try:
    from config.config import SCHEDULE_INTERVAL_MINUTES, REPORT_SCHEDULE_HOUR, HEALTH_CHECK_INTERVAL
    from src.etl_pipeline import WeatherETLPipeline
    from src.reporter import WeatherReporter
    from src.monitor import PipelineMonitor
except ImportError:
    from config import SCHEDULE_INTERVAL_MINUTES, REPORT_SCHEDULE_HOUR, HEALTH_CHECK_INTERVAL
    from etl_pipeline import WeatherETLPipeline
    from reporter import WeatherReporter
    from monitor import PipelineMonitor

logger = logging.getLogger(__name__)
_running = True


def _shutdown(sig, frame):
    global _running
    logger.info("Shutdown signal received.")
    _running = False


signal.signal(signal.SIGINT,  _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


def run_etl_job():
    logger.info("Scheduled ETL job triggered")
    WeatherETLPipeline().run()


def run_daily_report():
    logger.info("Daily report triggered")
    r = WeatherReporter()
    r.print_dashboard()
    r.generate_html_report()


def run_health_check():
    PipelineMonitor().run_health_check()


def start_scheduler():
    logger.info("Scheduler starting | ETL every %dmin | Report at %02d:00",
                SCHEDULE_INTERVAL_MINUTES, REPORT_SCHEDULE_HOUR)
    run_etl_job()
    run_health_check()
    schedule.every(SCHEDULE_INTERVAL_MINUTES).minutes.do(run_etl_job)
    schedule.every().day.at(f"{REPORT_SCHEDULE_HOUR:02d}:00").do(run_daily_report)
    schedule.every(HEALTH_CHECK_INTERVAL).seconds.do(run_health_check)
    while _running:
        schedule.run_pending()
        time.sleep(30)
    logger.info("Scheduler stopped.")
