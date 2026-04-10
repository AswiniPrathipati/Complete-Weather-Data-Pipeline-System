# src/api_client.py — OpenWeatherMap API Client
# ================================================

import requests
import logging
import time
from datetime import datetime

try:
    from config.config import API_KEY, BASE_URL, FORECAST_URL, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY
except ImportError:
    from config import API_KEY, BASE_URL, FORECAST_URL, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)


class WeatherAPIClient:
    """Handles all OpenWeatherMap API communication with retry logic."""

    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _get(self, url: str, params: dict) -> dict | None:
        params['appid'] = self.api_key
        params['units'] = 'metric'
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = self.session.get(url, params=params, timeout=API_TIMEOUT)
                r.raise_for_status()
                return r.json()
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code if e.response else 0
                if code == 401:
                    logger.error("Invalid API key.")
                    return None
                if code == 404:
                    logger.warning("City not found.")
                    return None
                if code == 429:
                    time.sleep(RETRY_DELAY * 2)
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout):
                logger.warning("Attempt %d failed", attempt)
            except requests.exceptions.RequestException as e:
                logger.error("Request error: %s", e)
                return None
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        return None

    def fetch_weather_by_coords(self, lat: float, lon: float, city_name: str) -> dict | None:
        raw = self._get(BASE_URL, {'lat': lat, 'lon': lon})
        return self._parse_current(raw, city_name) if raw else None

    def fetch_current_weather(self, city_name: str, country: str = 'IN') -> dict | None:
        raw = self._get(BASE_URL, {'q': f"{city_name},{country}"})
        return self._parse_current(raw, city_name) if raw else None

    def fetch_forecast(self, city_name: str, country: str = 'IN') -> list:
        raw = self._get(FORECAST_URL, {'q': f"{city_name},{country}"})
        if not raw or 'list' not in raw:
            return []
        return [self._parse_forecast_item(item, city_name) for item in raw['list']]

    def test_connection(self) -> bool:
        result = self._get(BASE_URL, {'q': 'London,GB'})
        ok = result is not None
        logger.info("API connectivity: %s", "PASS" if ok else "FAIL")
        return ok

    @staticmethod
    def _parse_current(data: dict, city_name: str) -> dict:
        return {
            'city':              city_name,
            'country':           data.get('sys', {}).get('country', 'IN'),
            'timestamp':         datetime.utcfromtimestamp(data.get('dt', 0)).isoformat(),
            'temperature_c':     data['main'].get('temp'),
            'feels_like_c':      data['main'].get('feels_like'),
            'temp_min_c':        data['main'].get('temp_min'),
            'temp_max_c':        data['main'].get('temp_max'),
            'humidity':          data['main'].get('humidity'),
            'pressure_hpa':      data['main'].get('pressure'),
            'wind_speed_mps':    data.get('wind', {}).get('speed'),
            'wind_direction':    data.get('wind', {}).get('deg'),
            'visibility_m':      data.get('visibility'),
            'cloudiness_pct':    data.get('clouds', {}).get('all'),
            'weather_condition': data['weather'][0].get('description') if data.get('weather') else None,
            'weather_icon':      data['weather'][0].get('icon') if data.get('weather') else None,
        }

    @staticmethod
    def _parse_forecast_item(item: dict, city_name: str) -> dict:
        return {
            'city':              city_name,
            'timestamp':         item.get('dt_txt'),
            'temperature_c':     item['main'].get('temp'),
            'humidity':          item['main'].get('humidity'),
            'pressure_hpa':      item['main'].get('pressure'),
            'wind_speed_mps':    item.get('wind', {}).get('speed'),
            'cloudiness_pct':    item.get('clouds', {}).get('all'),
            'weather_condition': item['weather'][0].get('description') if item.get('weather') else None,
        }
