import unittest
import pprint
from noms.client.client import Client
from noms.client.dict_parse import search_parse
from noms.client.dict_parse import food_parse


class TestDictParse(unittest.TestCase):

    def setUp(self):
        key = open("key.txt", "r").read()
        client = Client(key)

        self.client = client
        assert type(self.client) == Client

    def test_search_parse(self):
        pass

    def test_food_parse(self):
        pass
