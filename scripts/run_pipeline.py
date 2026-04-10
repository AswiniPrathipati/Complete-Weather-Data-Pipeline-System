#!/usr/bin/env python3
# scripts/run_pipeline.py — One-Click Pipeline Runner
# =====================================================
#
# Usage:
#   python scripts/run_pipeline.py run       ← run ETL once
#   python scripts/run_pipeline.py schedule  ← start scheduler
#   python scripts/run_pipeline.py report    ← print dashboard + HTML
#   python scripts/run_pipeline.py monitor   ← health check
#   python scripts/run_pipeline.py setup     ← init database only
#   python scripts/run_pipeline.py test      ← test API connectivity

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.logging_config  # noqa — must be first to set up logging

from src.etl_pipeline import WeatherETLPipeline
from src.reporter     import WeatherReporter
from src.monitor      import PipelineMonitor
from src.database     import setup_database
from src.api_client   import WeatherAPIClient

COMMANDS = {
    'run':      'Execute one ETL run',
    'schedule': 'Start the automated scheduler',
    'report':   'Print dashboard and save HTML report',
    'monitor':  'Run a pipeline health check',
    'setup':    'Initialise the database',
    'test':     'Test API connectivity',
}


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'

    if command == 'run':
        summary = WeatherETLPipeline().run()
        print("\n📋 Run Summary:")
        for k, v in summary.items():
            print(f"   {k:<25}: {v}")

    elif command == 'schedule':
        from src.scheduler import start_scheduler
        start_scheduler()

    elif command == 'report':
        r = WeatherReporter()
        r.print_dashboard()
        path = r.generate_html_report()
        print(f"\n💾 HTML report saved → {path}")

    elif command == 'monitor':
        PipelineMonitor().print_status()

    elif command == 'setup':
        setup_database()
        print("✅ Database initialised successfully.")

    elif command == 'test':
        ok = WeatherAPIClient().test_connection()
        if ok:
            print("✅ API connection successful!")
        else:
            print("❌ API connection failed. Check OPENWEATHER_API_KEY.")
            sys.exit(1)

    else:
        print("\n🌦️  Weather Data Pipeline — Available Commands:\n")
        for cmd, desc in COMMANDS.items():
            print(f"   python scripts/run_pipeline.py {cmd:<12}  {desc}")
        print()


if __name__ == "__main__":
    main()
