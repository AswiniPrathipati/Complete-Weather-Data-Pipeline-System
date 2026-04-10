# 🚀 Deployment & Maintenance Guide

## Local Development

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/weather-pipeline.git
cd weather-pipeline
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Set API key
export OPENWEATHER_API_KEY="your_key_here"

# 3. Run
python scripts/run_pipeline.py setup    # init DB
python scripts/run_pipeline.py test     # test API
python scripts/run_pipeline.py run      # one ETL run
python scripts/run_pipeline.py schedule # start scheduler
```

---

## Google Colab

1. Upload `Weather_Pipeline_Colab.ipynb` to [colab.research.google.com](https://colab.research.google.com)
2. In **Cell 2**, replace `YOUR_API_KEY_HERE` with your key
3. Click **Runtime → Run all**

---

## Running as a Background Service (Linux)

Create `/etc/systemd/system/weather-pipeline.service`:

```ini
[Unit]
Description=Weather Data Pipeline
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/weather-pipeline
Environment=OPENWEATHER_API_KEY=your_key_here
ExecStart=/opt/weather-pipeline/venv/bin/python scripts/run_pipeline.py schedule
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-pipeline
sudo systemctl start weather-pipeline
sudo systemctl status weather-pipeline
```

---

## Maintenance Scripts

### Reset the database
```bash
python scripts/reset_database.py
```

### Export data to CSV
```bash
python scripts/export_data.py
# Creates: reports/weather_export_YYYYMMDD.csv
```

---

## Monitoring

### Check health manually
```bash
python scripts/run_pipeline.py monitor
```

### View live logs
```bash
tail -f logs/pipeline.log
tail -f logs/monitor.log
```

### Log rotation
Logs rotate automatically at 5 MB with 5 backups kept (`config/logging_config.py`).

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `❌ Invalid API key` | Wrong or expired key | Re-check `OPENWEATHER_API_KEY` |
| `❌ City not found` | Typo in city name | Use lat/lon instead (already default) |
| `No data to display` | Pipeline not run yet | Run `python scripts/run_pipeline.py run` |
| `DB locked` | Two processes sharing DB | Stop duplicate processes |
| `Rate limit hit` | Too many API calls | Free tier allows 60 calls/min — pipeline waits automatically |

---

## Adding New Cities

In `config/config.py`, add to the `CITIES` list:
```python
{"name": "Mysore", "country": "IN", "lat": 12.2958, "lon": 76.6394},
```
Run the pipeline once — the city will be auto-inserted into the database.

---

## Changing Alert Thresholds

Edit `ALERT_THRESHOLDS` in `config/config.py`:
```python
ALERT_THRESHOLDS = {
    "high_temp":     40.0,   # raise from 35 to 40
    "high_humidity": 90,     # raise from 85 to 90
    ...
}
```
Changes take effect on the next pipeline run.
