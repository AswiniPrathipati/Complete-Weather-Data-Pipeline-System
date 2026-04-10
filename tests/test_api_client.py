# tests/test_api_client.py — Unit Tests: WeatherAPIClient Parser
# ================================================================

import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_client import WeatherAPIClient


MOCK_RESPONSE = {
    'dt': 1705305600,
    'main': {'temp': 28.5, 'feels_like': 30.0, 'temp_min': 26.0,
             'temp_max': 31.0, 'humidity': 65, 'pressure': 1013},
    'wind':    {'speed': 3.5, 'deg': 180},
    'clouds':  {'all': 20},
    'weather': [{'description': 'clear sky', 'icon': '01d'}],
    'visibility': 10000,
    'sys': {'country': 'IN'},
}


class TestAPIClientParser(unittest.TestCase):

    def setUp(self):
        self.client = WeatherAPIClient(api_key='test_key')

    def test_parse_temperature(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertEqual(parsed['temperature_c'], 28.5)

    def test_parse_humidity(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertEqual(parsed['humidity'], 65)

    def test_parse_city_name(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertEqual(parsed['city'], 'Mumbai')

    def test_parse_weather_condition(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertEqual(parsed['weather_condition'], 'clear sky')

    def test_parse_wind(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertEqual(parsed['wind_speed_mps'], 3.5)
        self.assertEqual(parsed['wind_direction'],  180)

    def test_parse_pressure(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertEqual(parsed['pressure_hpa'], 1013)

    def test_parse_missing_wind(self):
        data = dict(MOCK_RESPONSE); data['wind'] = {}
        parsed = self.client._parse_current(data, 'Delhi')
        self.assertIsNone(parsed['wind_speed_mps'])
        self.assertIsNone(parsed['wind_direction'])

    def test_parse_missing_weather_array(self):
        data = dict(MOCK_RESPONSE); data['weather'] = []
        parsed = self.client._parse_current(data, 'Chennai')
        self.assertIsNone(parsed['weather_condition'])

    def test_parse_country(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertEqual(parsed['country'], 'IN')

    def test_parse_timestamp_format(self):
        parsed = self.client._parse_current(MOCK_RESPONSE, 'Mumbai')
        self.assertIn('T', parsed['timestamp'])   # ISO format

    def test_parse_forecast_item(self):
        item = {
            'dt_txt': '2024-01-16 12:00:00',
            'main': {'temp': 25.0, 'humidity': 60, 'pressure': 1010},
            'wind': {'speed': 2.0},
            'clouds': {'all': 30},
            'weather': [{'description': 'partly cloudy'}]
        }
        parsed = self.client._parse_forecast_item(item, 'Hyderabad')
        self.assertEqual(parsed['city'],        'Hyderabad')
        self.assertEqual(parsed['temperature_c'], 25.0)
        self.assertEqual(parsed['weather_condition'], 'partly cloudy')


if __name__ == '__main__':
    unittest.main(verbosity=2)
