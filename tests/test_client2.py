import unittest
import pprint
from noms.client.client2 import Client2



class TestClient2(unittest.TestCase):

    def setUp(self):
        key = open("key.txt", "r").read()
        client = Client2(key)

        self.client = client
        assert type(self.client) == Client2

    def test_search(self):
        response, obj = self.client.foods_search("cheddar cheese")
        pprint.pprint(response)
        assert obj is not None

    def test_food_queries(self):

        # search single product
        response, obj = self.client.food('373052')
        pprint.pprint(response)
        assert obj is not None

        # search a list of products
        result = self.client.foods(['534358', '373052'])
        assert obj is not None

        # nothing found
        response, obj = self.client.food('11111100001111')
        assert obj is not None

        response, obj = self.client.foods(
                        {'373052': 100, '534358': 500, '747447': 100})
        assert obj is not None

        food_list = self.client.foods({
            '373052': 20,
            '534358': 100,
            ' 789510': 1000  # literally an entire liter of coke
        })
