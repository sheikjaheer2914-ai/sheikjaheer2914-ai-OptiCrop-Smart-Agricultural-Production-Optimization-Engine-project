import sys
import os

# Explicitly insert root and code directories to resolve background Pylance warnings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../5. Project Development Phase/code')))

import unittest
from app import app

class TestOptiCropSystemCore(unittest.TestCase):

    def setUp(self):
        """Initializes a sandboxed automation browser client layer."""
        self.app = app.test_client()
        self.app.testing = True

    def test_scenario_1_recommendation_matrix(self):
        """Verifies that Scenario 1 cleanly executes classification logic."""
        response = self.app.post('/predict', data={
            'scenario': '1', 'N': '90', 'P': '42', 'K': '43',
            'temperature': '20.8', 'humidity': '82', 'ph': '6.5', 'rainfall': '202'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scenario 1', response.data)

    def test_scenario_2_suitability_gaps(self):
        """Verifies that Scenario 2 triggers adaptive crop matching."""
        response = self.app.post('/predict', data={
            'scenario': '2', 'target_crop': 'maize', 'N': '90', 'P': '42', 'K': '43',
            'temperature': '20.8', 'humidity': '82', 'ph': '6.5', 'rainfall': '202'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scenario 2', response.data)

    def test_scenario_3_policy_insights(self):
        """Verifies that Scenario 3 maps macro strategy guidelines."""
        response = self.app.post('/predict', data={
            'scenario': '3', 'N': '15', 'P': '42', 'K': '43',
            'temperature': '20.8', 'humidity': '82', 'ph': '4.5', 'rainfall': '202'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scenario 3', response.data)

if __name__ == '__main__':
    unittest.main()
