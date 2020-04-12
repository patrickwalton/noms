import unittest
import pprint
from noms.client.client import Client
from noms.client.searchresults import SearchResults
from noms.objects.food import Food
from noms.objects.food import Meal


class Testing(unittest.TestCase):

    def setUp(self):
        key = open("key.txt", "r").read()
        client = Client(key)

        self.client = client
        assert type(self.client) == Client

        # self.meal = self.meal()
        # self.pantry = self.pantry()

    def test_search(self):
        client = self.client
        broc_search = client.search_query("Broccoli")
        assert "items" in broc_search.json.keys()
        assert len(broc_search.json["items"]) > 5
        uni_search = client.search_query("Unicorn meat")
        pprint.pprint(uni_search)
        # assert uni_search == None

    def test_foods(self):
        client = self.client
        food_list = client.get_foods({'11090':100, '20041':500, '09120319':100})
        assert len(food_list) == 2
        food_list = client.get_foods({
            '01001':20,
            '01132':100,
            '09037':80,
            '15076':150,
            '09201':140,
            '14278':300,
            '12006':20,
            '20041':150,
            '16057':50,
            '11233':50,
            '19904':10,
            '14400':1000 # literally an entire liter of coke
        })
        assert len(food_list) == 12
        assert type(food_list[0]) == Food
        assert "name" in food_list[0].desc.keys()

    def meal(self):
        client = self.client
        food_list = client.get_foods({
            '01001':20,
            '01132':100,
            '09037':80,
            '15076':150,
            '09201':140,
            '14278':300,
            '12006':20,
            '20041':150,
            '16057':50,
            '11233':50,
            '19904':10,
            '14400':1000 # literally an entire liter of coke
        })
        if food_list is None:
            raise Exception("NPE on client.get_foods()")
        meal = Meal(food_list)
        assert type(meal) == noms.Meal
        assert len(meal.foods) == 12
        return meal

    def test_report(meal):
        r = noms.report(meal)
        assert len(r) == len(noms.nutrient_dict)

    def test_sort(meal):
        m = copy.deepcopy(meal)
        m.sort_by_top("Sugar")
        assert m.foods[0].desc["ndbno"] == '14400' # the most sugar-dense food in the meal is coke

    def pantry(self):
        client = self.client
        pantry_items = {
        # DAIRY AND EGG
        "01001":100, # butter, salted
        "01145":100, # butter, without salt
        "01079":100, # 2% milk
        "01077":100, # milk, whole
        "01086":100, # skim milk
        "01132":100, # scrambled eggs
        "01129":100, # hard boiled eggs
        "01128":100, # fried egg
        # MEAT
        "15076":100, # atlantic salmon
        "07935":100, # chicken breast oven-roasted
        "13647":100, # steak
        "05192":100, # turkey
        # FRUIT
        "09037":100, # avocado
        "09316":100, # strawberries
        "09050":100, # blueberry
        "09302":100, # raspberry
        "09500":100, # red delicious apple
        "09040":100, # banana
        "09150":100, # lemon
        "09201":100, # oranges
        "09132":100, # grapes
        # PROCESSED
        "21250":100, # hamburger
        "21272":100, # pizza
        "19088":100, # ice cream
        "18249":100, # donut
        # DRINK
        "14400":100, # coke
        "14429":100, # tap water
        "14433":100, # bottled water
        "09206":100, # orange juice
        "14278":100, # brewed green tea
        "14209":100, # coffee brewed with tap water
        # (milk is included in dairy group)
        # GRAIN
        "12006":100, # chia
        "12220":100, # flaxseed
        "20137":100, # quinoa, cooked
        "20006":100, # pearled barley
        "20051":100, # white rice enriched cooked
        "20041":100, # brown rice cooked
        "12151":100, # pistachio
        "19047":100, # pretzel
        "12061":100, # almond
        # LEGUME
        "16057":100, # chickpeas
        "16015":100, # black beans
        "16043":100, # pinto beans
        "16072":100, # lima beans
        "16167":100, # peanut butter smooth
        # VEGETABLE
        "11124":100, # raw carrots
        "11090":100, # broccoli
        "11457":100, # spinach, raw
        "11357":100, # baked potato
        "11508":100, # baked sweet potato
        "11530":100, # tomato, red, cooked
        "11253":100, # lettuce
        "11233":100, # kale
        "11313":100, # peas
        "11215":100, # garlic
        # OTHER
        "04053":100, # olive oil
        "19904":100, # dark chocolate
        "11238":100, # shiitake mushrooms
        "19165":100, # cocoa powder
        }
        pantry_food = client.get_foods(pantry_items)
        pantry = noms.Meal(pantry_food)
        assert type(pantry) == noms.Meal
        assert pantry.nutrients[0]["name"] == noms.nutrient_dict[0]["name"]
        return pantry

    def test_gen_recommendations(meal, pantry, verbose=False):
        recommendations = noms.generate_recommendations(meal, pantry, noms.nutrient_dict, 3, verbose)
        pre_meal_loss = noms.analyze.loss(meal, noms.nutrient_dict)
        post_meal = noms.Meal(meal.foods + [pantry[recommendations[0][1]]])
        post_meal_loss = noms.analyze.loss(post_meal, noms.nutrient_dict)
        # check that the loss of the new meal is lower
        assert post_meal_loss < pre_meal_loss

    def test_remove_recommendation(meal):
        result = noms.recommend_removal(meal, noms.nutrient_dict)
        # check that we are recommending the user not to have a liter of coke
        assert meal.foods[result].desc["ndbno"] == "14400"

    def test_all():
        _client()
        _search()
        _foods()
        meal = _meal()
        _report(meal)
        _sort(meal)
        pantry = _pantry()
        _gen_recommendations(meal, pantry.foods)
        _remove_recommendation(meal)
