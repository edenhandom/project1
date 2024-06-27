import unittest
from unittest.mock import patch
import perenual_api
import sqlite3

class TestPlantMatching(unittest.TestCase):
    @patch('perenual_api.requests.get')
    def setUp(self, mock_get):
        mock_get.side_effect = [
            unittest.mock.Mock(status_code=200, json=lambda: {'data': [{'id': 1}, {'id': 2}, {'id': 3}]}),
            unittest.mock.Mock(status_code=200, json=lambda: {
                'id': 1, 'common_name': 'Rose', 'scientific_name': ['Rosa'], 'sunlight': ['full sun'],
                'watering': 'frequent', 'watering_period': 'weekly', 'maintenance': 'moderate',
                'description': 'A rose is a woody perennial flowering plant of the genus Rosa, in the family Rosaceae, or the flower it bears.',
                'type': 'flowering'
            })
        ]

        perenual_api.create_tables() 

    @patch('perenual_api.requests.get')
    def test_store_plant_ids(self, mock_get):
        mock_get.return_value = unittest.mock.Mock(
            status_code=200, 
            json=lambda: {'data': [{'id': 1}, {'id': 2}, {'id': 3}]}
        )

        perenual_api.store_plant_ids()

        conn = sqlite3.connect('plants.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM plant_id')
        stored_ids = [row[0] for row in cursor.fetchall()]

        self.assertEqual(stored_ids, [1, 2, 3])

    @patch('perenual_api.requests.get')
    def test_store_plant_data(self, mock_get):
        mock_get.return_value = unittest.mock.Mock(
            status_code=200,
            json=lambda: {
                'id': 1, 'common_name': 'Rose', 'scientific_name': ['Rosa'], 'sunlight': ['full sun'],
                'watering': 'frequent', 'watering_period': 'weekly', 'maintenance': 'moderate', 
                'description': 'A rose is a woody perennial flowering plant of the genus Rosa, in the family Rosaceae, or the flower it bears.',
                'type': 'flowering'
            }
        )

        perenual_api.store_plant_data(1)

        conn = sqlite3.connect('plants.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM plant_data WHERE id = 1')
        stored_data = cursor.fetchone()

        expected_data = (
            1, 'Rose', 'Rosa', 'full sun', 'frequent', 'weekly', 'moderate', 
            'A rose is a woody perennial flowering plant of the genus Rosa, in the family Rosaceae, or the flower it bears.', 
            'flowering'
        )
        self.assertEqual(stored_data[:9], expected_data)

    @patch('perenual_api.input', create=True)
    @patch('perenual_api.print')
    def test_match_plants(self, mock_print, mock_input):
        mock_input.side_effect = ['full sun', 'frequent', 'moderate']

        perenual_api.store_plant_ids()

        perenual_api.store_plant_data(1)

        perenual_api.match_plants('full sun', 'frequent', 'moderate')
    

if __name__ == '__main__':
    unittest.main()