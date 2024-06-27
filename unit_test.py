import unittest
from unittest.mock import patch, MagicMock
import sqlite3
from perenual_api import create_tables, store_plant_ids, store_plant_data, match_plants


class TestPlantMatching(unittest.TestCase):
    def test_store_plant_ids(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 2

    def test_function2(self):
        self.assertEqual(function2(2,1), 3)
        self.assertEqual(function2(2.1, 1.2), 3.3)

if __name__ == '__main__':
    unittest.main()