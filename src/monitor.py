# src/monitor.py — Pipeline Health Monitoring
# =============================================

import logging
import os
from datetime import datetime

try:
    from config.config import MONITOR_LOG, MAX_CONSECUTIVE_FAILURES, DB_PATH
    from src.database import get_connection
except ImportError:
    from config import MONITOR_LOG, MAX_CONSECUTIVE_FAILURES, DB_PATH
    from database import get_connection

logger = logging.getLogger(__name__)


class PipelineMonitor:

    def run_health_check(self) -> dict:
        checks = {
            'database_accessible':   self._check_database(),
            'data_freshness':        self._check_freshness(),
            'recent_run_status':     self._check_recent_runs(),
            'consecutive_failures':  self._count_consecutive_failures(),
            'disk_space_mb':         self._check_disk_space(),
        }
        cf = checks['consecutive_failures']
        fr = checks['recent_run_status'].get('failure_rate_pct', 0)
        overall = ('CRITICAL' if not checks['database_accessible'] or cf >= MAX_CONSECUTIVE_FAILURES
                   else 'WARNING' if not checks['data_freshness'].get('is_fresh') or fr > 30
                   else 'HEALTHY')
        report = {'timestamp': datetime.now().isoformat(), 'overall_status': overall, 'checks': checks}
        self._write_log(report)
        return report

    def print_status(self):
        report = self.run_health_check()
        icon = {'HEALTHY': '✅', 'WARNING': '⚠️', 'CRITICAL': '🔴'}.get(report['overall_status'], '❓')
        print(f"\n{icon}  Pipeline Health: {report['overall_status']}")
        print(f"   Timestamp : {report['timestamp']}")
        for k, v in report['checks'].items():
            print(f"   {k:<30}: {v}")
        print()

    def _check_database(self):
        try:
            if not os.path.exists(DB_PATH): return False
            conn = get_connection(); conn.execute("SELECT 1"); conn.close()
            return True
        except Exception: return False

    def _check_freshness(self, max_hours=3):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT MAX(timestamp) AS ts FROM weather_data WHERE is_valid=1")
            latest = cur.fetchone()['ts']; conn.close()
            if not latest: return {'is_fresh': False, 'latest_record': None}
            age = (datetime.utcnow() - datetime.fromisoformat(latest)).total_seconds() / 3600
            return {'is_fresh': age <= max_hours, 'latest_record': latest, 'age_hours': round(age, 2)}
        except Exception as e:
            return {'is_fresh': False, 'error': str(e)}

    def _check_recent_runs(self, limit=10):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute('''SELECT status,duration_seconds,run_timestamp
                FROM pipeline_logs ORDER BY run_timestamp DESC LIMIT ?''', (limit,))
            rows = [dict(r) for r in cur.fetchall()]; conn.close()
            if not rows: return {'total_runs': 0}
            s = sum(1 for r in rows if r['status']=='SUCCESS')
            return {'total_runs': len(rows), 'successes': s, 'failures': len(rows)-s,
                    'failure_rate_pct': round(100*(len(rows)-s)/len(rows), 1),
                    'avg_duration_sec': round(sum(r['duration_seconds'] or 0 for r in rows)/len(rows), 2),
                    'last_run_status': rows[0]['status'], 'last_run_time': rows[0]['run_timestamp']}
        except Exception as e: return {'error': str(e)}

    def _count_consecutive_failures(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT status FROM pipeline_logs ORDER BY run_timestamp DESC LIMIT 20")
            rows = cur.fetchall(); conn.close()
            count = 0
            for r in rows:
                if r['status'] == 'FAILED': count += 1
                else: break
            return count
        except Exception: return 0

    def _check_disk_space(self):
        try:
            stat = os.statvfs('.')
            return round(stat.f_bavail * stat.f_frsize / (1024**2), 1)
        except Exception: return -1.0

    def _write_log(self, report):
        os.makedirs(os.path.dirname(MONITOR_LOG), exist_ok=True)
        with open(MONITOR_LOG, 'a', encoding='utf-8') as f:
            f.write(f"\n[{report['timestamp']}] {report['overall_status']} | {report['checks']}\n")
