import unittest
import pprint
from noms.client.client2 import Client2


import logging
import contextlib

from http.client import HTTPConnection   # py3

def debug_requests_on():
    '''Switches on logging of the requests module.'''
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def debug_requests_off():
    '''Switches off logging of the requests module, might be some side-effects'''
    HTTPConnection.debuglevel = 0

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.handlers = []
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARNING)
    requests_log.propagate = False

@contextlib.contextmanager
def debug_requests():
    '''Use with 'with'!'''
    debug_requests_on()
    yield
    debug_requests_off()

class TestClient2(unittest.TestCase):

    def setUp(self):
        key = open("key.txt", "r").read()
        key = key.strip()
        client = Client2(key)
        # debug_requests_on()

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
