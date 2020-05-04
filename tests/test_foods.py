import unittest
import pprint
from noms.client.client2 import Client2
from noms.client.foods import Foods


class TestFoods(unittest.TestCase):

    def setUp(self):
        key = open("key.txt", "r").read()
        key = key.strip()
        client = Client2(key)
        foods = Foods(client)

        self.foods = foods

    def test_exact_match(self):
        results, unfiltered = self.foods.exact_match("cucumber")
        if len(results) == 0:
            print("no exact match was possible!")
            for r in results:
                print("%s -> %s" % (r["description"], r["ingredients"]))

        print("results: %s" % len(results))
        for r in results:
            try:
                print("%s -> %s" % (r["description"], r["ingredients"]))
            except Exception:
                pprint.pprint(results)

    def test_find_organic(self):

        search = ["broccoli", "carrots", "potatoes", "egg", "cauliflower",
                  "cucumber", "paprika", "pepper", "ginger", "cinnamon",
                  "strawberries"]

        search = ["bean sauce",
        "bean sprouts",
        "beaten eggs",
        "bechamel",
        "beef bouillon granules",
        "beef consomme"]

        for s in search:
            # print("look for %s..." % s)
            r = self.foods.find_organic(s)
            try:
                print("%s -> %s / %s, nutr_count = %s" % (r["description"], r["fdcId"], r['dataType'], len(r["foodNutrients"])))
            except Exception as e:
                print(e)
                print("result keys")
                pprint.pprint(r.keys())
