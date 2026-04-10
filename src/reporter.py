# src/reporter.py — Report Generation & Analytics
# ==================================================

import os
import logging
from datetime import datetime

try:
    from config.config import REPORTS_DIR
    from src.database import get_connection, get_latest_weather, get_database_stats
except ImportError:
    from config import REPORTS_DIR
    from database import get_connection, get_latest_weather, get_database_stats

logger = logging.getLogger(__name__)
os.makedirs(REPORTS_DIR, exist_ok=True)


class WeatherReporter:

    def city_avg_temperature(self, days=30):
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute('''SELECT c.city_name,
            ROUND(AVG(w.temperature_c),2) AS avg_temp,
            ROUND(MAX(w.temperature_c),2) AS max_temp,
            ROUND(MIN(w.temperature_c),2) AS min_temp,
            COUNT(*) AS record_count
            FROM weather_data w JOIN cities c ON w.city_id=c.city_id
            WHERE w.is_valid=1 AND w.timestamp>=datetime('now',? || ' days')
            GROUP BY c.city_name ORDER BY avg_temp DESC''', (f'-{days}',))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def recent_alerts(self, limit=20):
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute('''SELECT a.*,c.city_name FROM weather_alerts a
            JOIN cities c ON a.city_id=c.city_id
            WHERE a.is_resolved=0 ORDER BY a.triggered_at DESC LIMIT ?''', (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def print_dashboard(self):
        stats   = get_database_stats()
        current = get_latest_weather()
        alerts  = self.recent_alerts(10)

        print("\n" + "=" * 60)
        print("       WEATHER DATA PIPELINE SYSTEM — DASHBOARD")
        print("=" * 60)
        print(f"📊 System Status  : RUNNING")
        print(f"⏰ Report Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗄️  Total Records  : {stats.get('total_records', 0):,}")
        print(f"🏙️  Cities Tracked : {stats.get('active_cities', 0)}")
        print(f"✅ Data Quality   : {stats.get('data_quality_pct', 0)}%")
        print(f"🔔 Open Alerts    : {stats.get('open_alerts', 0)}")
        print(f"📅 Last Record    : {stats.get('last_record_time', 'N/A')}")

        print("\n🌤️  CURRENT WEATHER SNAPSHOT:")
        print("-" * 60)
        for row in current:
            icon = self._icon(row.get('weather_condition', ''))
            print(f"  {icon} {row['city_name']:<14} "
                  f"{row.get('temperature_c','?'):.1f}°C  "
                  f"💧{row.get('humidity','?')}%  "
                  f"💨{row.get('wind_speed_mps','?')} m/s  "
                  f"[{row.get('temp_label','?')}]  "
                  f"{str(row.get('weather_condition','')).title()}")

        print("\n🚨 ACTIVE ALERTS:")
        print("-" * 60)
        if alerts:
            for a in alerts:
                icon = "🔴" if a['severity'] == 'WARNING' else "🟡"
                print(f"  {icon} [{a['alert_type']}] {a['alert_message']}")
        else:
            print("  ✅ No active alerts.")

        avgs = self.city_avg_temperature()
        if avgs:
            print("\n📈 TEMPERATURE RANKING (Last 30 days):")
            print("-" * 60)
            for i, r in enumerate(avgs, 1):
                print(f"  {i:>2}. {r['city_name']:<14} Avg: {r['avg_temp']}°C  "
                      f"(Max: {r['max_temp']}°C / Min: {r['min_temp']}°C)")
        print("\n" + "=" * 60 + "\n")

    def generate_html_report(self) -> str:
        stats   = get_database_stats()
        current = get_latest_weather()
        alerts  = self.recent_alerts()
        avgs    = self.city_avg_temperature()
        ts      = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        rows_html   = ''.join(f"""<tr><td>{r.get('city_name','')}</td>
            <td>{r.get('temperature_c',''):.1f} °C</td>
            <td>{r.get('humidity','')} %</td>
            <td>{r.get('pressure_hpa','')} hPa</td>
            <td>{r.get('wind_speed_mps','')} m/s</td>
            <td>{str(r.get('weather_condition','')).title()}</td>
            <td>{r.get('temp_label','')}</td></tr>""" for r in current)

        alerts_html = ''.join(f"""<tr>
            <td style='color:{"#e74c3c" if a["severity"]=="WARNING" else "#f39c12"}'><b>{a['alert_type']}</b></td>
            <td>{a.get('city_name','')}</td><td>{a['alert_message']}</td>
            <td>{a['triggered_at']}</td></tr>""" for a in alerts) or \
            "<tr><td colspan='4'>✅ No active alerts.</td></tr>"

        avg_html = ''.join(f"""<tr><td>{r['city_name']}</td>
            <td>{r['avg_temp']} °C</td><td>{r['max_temp']} °C</td>
            <td>{r['min_temp']} °C</td><td>{r['record_count']}</td></tr>""" for r in avgs)

        html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Weather Pipeline Report – {ts}</title>
<style>body{{font-family:Arial,sans-serif;background:#f4f6f8;color:#333;padding:24px}}
h1{{color:#2c3e50}}h2{{color:#2980b9;border-bottom:2px solid #2980b9;padding-bottom:6px}}
.grid{{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:28px}}
.card{{background:#fff;border-radius:8px;padding:18px 24px;box-shadow:0 2px 6px rgba(0,0,0,.1);min-width:140px}}
.card .val{{font-size:2em;font-weight:bold;color:#2980b9}}.card .lbl{{font-size:.85em;color:#888}}
table{{border-collapse:collapse;width:100%;background:#fff;border-radius:8px;
       box-shadow:0 2px 6px rgba(0,0,0,.1);margin-bottom:28px}}
th{{background:#2980b9;color:#fff;padding:10px 14px;text-align:left}}
td{{padding:8px 14px;border-bottom:1px solid #eee}}tr:hover td{{background:#f0f4ff}}</style></head>
<body><h1>🌦️ Weather Data Pipeline Report</h1><p>Generated: {ts}</p>
<h2>📊 System Statistics</h2><div class="grid">
<div class="card"><div class="val">{stats.get('total_records',0):,}</div><div class="lbl">Total Records</div></div>
<div class="card"><div class="val">{stats.get('active_cities',0)}</div><div class="lbl">Cities Tracked</div></div>
<div class="card"><div class="val">{stats.get('data_quality_pct',0)}%</div><div class="lbl">Data Quality</div></div>
<div class="card"><div class="val">{stats.get('open_alerts',0)}</div><div class="lbl">Open Alerts</div></div>
</div>
<h2>🌤️ Current Weather</h2>
<table><tr><th>City</th><th>Temp</th><th>Humidity</th><th>Pressure</th><th>Wind</th><th>Condition</th><th>Label</th></tr>
{rows_html}</table>
<h2>🚨 Active Alerts</h2>
<table><tr><th>Type</th><th>City</th><th>Message</th><th>Triggered</th></tr>{alerts_html}</table>
<h2>📈 Temperature Analysis (30 days)</h2>
<table><tr><th>City</th><th>Avg</th><th>Max</th><th>Min</th><th>Records</th></tr>
{avg_html}</table></body></html>"""

        fname = os.path.join(REPORTS_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info("Report saved: %s", fname)
        return fname

    @staticmethod
    def _icon(c):
        c = (c or '').lower()
        if 'rain'  in c: return '🌧️'
        if 'cloud' in c: return '☁️'
        if 'clear' in c: return '☀️'
        if 'snow'  in c: return '❄️'
        if 'storm' in c: return '⛈️'
        if 'mist'  in c or 'fog' in c: return '🌫️'
        return '🌤️'
