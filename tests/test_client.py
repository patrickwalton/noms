import unittest
import pprint
from noms.client.client import Client


class TestClient(unittest.TestCase):

    def setUp(self):
        key = open("key.txt", "r").read()
        client = Client(key)

        self.client = client
        assert type(self.client) == Client

    def test_search(self):
        self.client.search_query("cheddar cheese")

    def test_food_query(self):

        # search single product
        result = self.client.food_query('373052')
        assert 1 == len(result['foods'])

        # search a list of products
        result = self.client.food_query(['534358', '373052'])
        assert 2 == len(result['foods'])

        # nothing found
        result = self.client.food_query('11111100001111')

    def test_get_foods(self):

        food_list = self.client.get_foods(
                        {'373052': 100, '534358': 500, '747447': 100})
        assert len(food_list) == 2
        food_list = self.client.get_foods({
            '373052': 20,
            '534358': 100,
            ' 789510': 1000  # literally an entire liter of coke
        })
        assert len(food_list) == 12
