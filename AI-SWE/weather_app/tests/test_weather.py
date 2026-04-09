import unittest
from src.weather_api import get_coordinates, get_weather

class TestWeatherAPI(unittest.TestCase):
    def test_get_coordinates_valid(self):
        lat, lon = get_coordinates("Rome")
        self.assertIsNotNone(lat)
        self.assertIsNotNone(lon)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

    def test_get_coordinates_invalid(self):
        lat, lon = get_coordinates("InvalidCity123")
        self.assertIsNone(lat)
        self.assertIsNone(lon)

    def test_get_weather_valid(self):
        data = get_weather("Rome")
        self.assertIsInstance(data, dict)
        self.assertNotIn("error", data)
        self.assertIn("temperature", data)
        self.assertIn("humidity", data)
        self.assertIn("daily", data)
        daily = data["daily"]
        self.assertIn("dates", daily)
        self.assertIn("max_temps", daily)
        self.assertIn("min_temps", daily)
        self.assertIn("codes", daily)

    def test_get_weather_invalid(self):
        data = get_weather("InvalidCity123")
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()