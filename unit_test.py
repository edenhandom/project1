import unittest
from unittest.mock import patch, MagicMock
import sqlite3
from perenual_api import create_tables, store_plant_ids, store_plant_data, match_plants


class TestPlantMatching(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory')
        self.cursor = self.conn.cursor()
        create_tables(self.conn, self.cursor)

    def setDown(self):
        self.conn.close()

    @patch('yourCodeFileName.requests.get')
    def test_store_plant_ids(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                { 'id': 1, 'type' : 'flower'},
                {'id': 2, 'type' : 'tree'},
                {'id': 3, 'type' : 'herb'},
            ]
        }
        mock_get.return_value = mock_response
        perenual_api.store_plant_ids()

        self.cursor.execute('SELECT id FROM plant_id')
        stored_ids = [row[0] for row in self.cursor.fetchall()]
        self.assertEqual(stored_ids, [1, 3])

    @patch('yourCodeFileName.requests.get')
    def test_store_plant_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'common_name': 'Rose',
            'scientific_name': ['Rosa'],
            'sunlight': ['full sun'],
            'watering': 'moderate',
            'watering_period': 'morning',
            'maintenance': 'low',
            'type': 'flower'
        }
        mock_get.return_value = mock_response

        perenual_api.store_plant_data(1)

        self.cursor.execute('SELECT * FROM plant_data WHERE id = 1')
        stored_data = self.cursor.fetchone()
        expected_data = (1, 'Rose', 'Rosa', 'full sun', 'moderate', 'morning', 'low', 'flower')
        self.assertEqual(stored_data[:8], expected_data)

    @patch('yourCodeFileName.input', mock_user_input=['full sun', 'moderate', 'weekly', 'low', 'flower'])
    def test_match_plants(self, mock, input):
        self.cursor.execute('''
        INSERT INTO plant_data (id, common_name, scientific_name, sunlight, watering, watering_period, maintenance, type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1, 'Rose', 'Rosa', 'full sun', 'moderate', 'morning', 'low', 'flower'))
        self.conn.commit()

        with patch('builtins.print') as mock_print:
            yourCodeFileName.match_plants()
            mock_print.assert_any_call("\nMatching Plants:")
            mock_print.assert_any_call("Common Name: Rose, Scientific Name: Rosa, Sunlight: full sun, "
                                       "Watering: moderate, Watering period: morning, Maintenance: low, Type: flower")

if __name__ == '__main__':
    unittest.main()
