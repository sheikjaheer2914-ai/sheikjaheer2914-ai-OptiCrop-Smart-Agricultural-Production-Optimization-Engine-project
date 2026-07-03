import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../5. Project Development Phase/code')))
from app import app

class TestOptiCropApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_scenario_1_recommendation(self):
        response = self.app.post('/predict', data={
            'scenario': '1', 'N': '90', 'P': '42', 'K': '43',
            'temperature': '20.8', 'humidity': '82', 'ph': '6.5', 'rainfall': '202'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scenario 1', response.data)

    def test_scenario_3_automatic_alerts(self):
        response = self.app.post('/predict', data={
            'scenario': '3', 'N': '15', 'P': '42', 'K': '43',
            'temperature': '20.8', 'humidity': '82', 'ph': '4.5', 'rainfall': '202'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Automated Soil Health Warnings', response.data)

if __name__ == '__main__':
    unittest.main()
