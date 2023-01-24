"""Client class to interface with FoodData Central.
FoodData Central requires a Data.gov key: https://api.data.gov/signup/
"""

from enum import Enum
import json
import time
import requests


import copy
# from nutrient_dict import nutrient_dict, index_from_name

import pprint

BASE_URL = 'https://api.nal.usda.gov/fdc/v1'
DATA_TYPES = [
    'Foundation',
    'SR Legacy',
    'Branded',
    'Survey (FNDDS)'
]


class DataType(Enum):
    Foundation = 'Foundation'
    SR = 'SR Legacy'          # USDA Standard Refernece
    Branded = 'Branded'
    FNDDS = 'Survey (FNDDS)'


class Format(Enum):
    abridged = 'abridged' # shortened list of elements
    full = 'full'         # default. all elements


class Sorting(Enum):
    """Options for sorting results
    """
    dataType = 'dataType.keyword'
    description = 'lowercaseDescription.keyword'
    fdcId = 'fdcId'
    publishedDate = 'publishedDate'
    score = 'score'


# https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
def mergedicts(a, b, path=None):
    """merges b into a"""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                mergedicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key] = a[key] + b[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def norm_rda(nutrient_array, nutrient_dict, disp=False):
    r_nut = copy.deepcopy(nutrient_array)
    for ni, _ in enumerate(nutrient_dict):
        norm_val = 0
        if nutrient_dict[ni]['rda'] != None:
            if r_nut[ni]['value'] < nutrient_dict[ni]['rda']:
                # value is 5, rda is 15
                # norm value is 5/15 = 0.33
                r_nut[ni].update(to="rda")
                norm_val = r_nut[ni]['value']/nutrient_dict[ni]['rda']
            else:
                # value is 30, rda is 15
                # norm value is 1
                r_nut[ni].update(to="rda")
                norm_val = 1
        if nutrient_dict[ni]['limit'] != None:
            if r_nut[ni]['value'] > nutrient_dict[ni]['limit']:
                r_nut[ni].update(to="limit")
                norm_val = r_nut[ni]['value']/nutrient_dict[ni]['limit']
            elif nutrient_dict[ni]['rda'] == None:
                if disp:
                    r_nut[ni].update(to="limit")
                    norm_val = r_nut[ni]['value']/nutrient_dict[ni]['limit']
                else:
                    norm_val = 1
        r_nut[ni].update(value=norm_val)
        if 'measures' in r_nut[ni].keys():
            del r_nut[ni]['measures']
        del r_nut[ni]['unit']
    return r_nut

class Portion:
    def __init__(self, portion_data):
        if 'amount' in portion_data.keys():
            amount = float(portion_data['amount'])
        else:
            amount = 1
        self.weight = float(portion_data['gramWeight'])*amount
        self.unit = '(' + str(amount) + 'X) ' + str(portion_data['modifier'])

    def __str__(self):
        return self.unit + ' = ' + str(self.weight) + 'g'
    
    def __repr__(self):
        return "<Portion: " + self.__str__() + ">"

class Food:
    def __init__(self, food_data):
        self.id = food_data['fdcId']
        self.description = food_data["description"]
        self.nutrients = food_data["foodNutrients"]
        if 'foodPortions' in food_data.keys():
            self.portions = [Portion(portion_data) for portion_data in food_data["foodPortions"]]
        else:
            self.portions = []

    def norm_rda(self, nutrient_dict):
        return norm_rda(self.nutrients, nutrient_dict)
    
    def __str__(self):
        return self.description
    
    def __repr__(self):
        return "<Food: " + self.description + " " + str(self.id) + ">"
    
class Meal:
    def __init__(self, foods):
        self.foods = foods
        self.nutrients = []
        for nutrient in foods[0].nutrients:
            to_app = nutrient.copy()
            to_app["value"] = 0
            self.nutrients.append(to_app)
        for food in foods:
            n = 0
            for nutrient in food.nutrients:
                self.nutrients[n]["value"] += nutrient["value"]
                n += 1
        for ni, _ in enumerate(self.nutrients):
            self.nutrients[ni]["value"] = self.nutrients[ni]["value"]
    # def sort_by_top(self, n):
    #     ni = index_from_name(n)
    #     self.foods.sort(key=lambda f: f.nutrients[ni]["value"], reverse=True)
    def norm_rda(self, nutrient_dict, disp=False):
        return norm_rda(self.nutrients, nutrient_dict, disp)

class Client:
    def __init__(self, api_key="DEMO_KEY"):
        self.api_key = api_key

        if api_key == "DEMO_KEY":
            self.interval = 3600/30
        else:
            self.interval = 3600/1000 # API says it's rate limited at 1000 requests per hour, but the header says tells me 3600. TODO: dynamically get this by making a dummy request.

        self.remaining_requests = 3600

    def process_args(self, **kwargs):
        """Process and validate arguments from any endpoint.

        # Arguments per endpoint

            ## Food and Foods
            format:: Format enum
            nutrients:: list

                ### Just Food
                fdcId:: string

                ### Just Foods
                fdcIds:: list

            ## Foods List and Foods Search
            dataTypes:: list
            sortBy:: Sorting enum
            reverse:: bool (corresponds to sortOrder in API spec)
            pageSize:: int
            pageNumber:: int

                ### Just Foods Search
                query:: str
                brandOwner:: str
        """
        data = {}

        if 'format' in kwargs:
            _format = kwargs['format']
            _nutrients = kwargs['nutrients']
            assert isinstance(_format, Format), \
                f"'format' arg should be an instance of the noms.Format enum class. format object was {_format} instead."
            data.update({'format': _format.value})

        if 'nutrients' in kwargs:
            # TODO: check against an internal register of all nutrients
            if _nutrients is not None:
                _nutrients = kwargs['nutrients']
                data.update({'nutrients': _nutrients})

        if 'fdcId' in kwargs:
            # TODO: validate this and the next under constraints
            _fdcId = kwargs['fdcId']
            data.update({'fdcId': _fdcId})

        if 'fdcIds' in kwargs:
            _fdcIds = kwargs['fdcIds']
            data.update({'fdcIds': _fdcIds})

        if 'dataTypes' in kwargs:
            _dataTypeEnums = kwargs['dataTypes']
            _dataTypes = []
            for dt in _dataTypeEnums:
                assert isinstance(dt, DataType), \
                    f"'dataType' should be a list of noms.DataType enums. '{dt}' not understood."
                _dataTypes.append(dt.value)

            # this statement leads to a 400 error - USDA confirms a documentation error.
            data.update({'dataType': ','.join(_dataTypes)})
            # nees to use nested JSON instead!
            data.update({'dataType': _dataTypes})
            # data.update({'dataType': _dataTypes})
            # data.update({'dataType': "Foundation,SR Legacy"})

        if 'sortBy' in kwargs:
            _sortBy = kwargs['sortBy']
            assert isinstance(_sortBy, Sorting), \
                f"'sortBy' arg should be an instance of the noms.Sorting enum class. sortBy object was {_sortBy} instead."
            data.update({'sortBy': _sortBy.value})

        if 'reverse' in kwargs:
            data.update({'sortOrder': 'asc' if not kwargs['reverse'] else 'desc'})

        if 'pageSize' in kwargs:
            _pageSize = kwargs['pageSize']
            assert _pageSize >= 1, f"pageSize must be at least one. pageSize was {_pageSize}"
            if _pageSize > 200:
                print(f"Warning: maximum page size is 200. pageSize passed is {_pageSize}")
            data.update({'pageSize': _pageSize})

        if 'pageNumber' in kwargs:
            _pageNumber = kwargs['pageNumber']
            data.update({'pageNumber': _pageNumber})

        if 'query' in kwargs:
            _query = kwargs['query']
            data.update({'query': _query})

        if 'brandOwner' in kwargs:
            _brandOwner = kwargs['brandOwner']
            if _brandOwner is not None:
                data.update({'brandOwner': _brandOwner})

        return data

    def food(self,
             fdcId: str):
        """Retrieves a single food item by an FDC ID.
            """

        if self.remaining_requests < 10:
                time.sleep(self.interval)

        for i in range(10):
            if i == 1:
                print("    (Trying to connect to API ", end="")
            elif i > 1:
                print(".", end="")
                time.sleep(self.interval)

            response = self.api_get("/food/" + str(fdcId))

            obj = json.loads(response.text) if response.status_code == 200 else None

            self.remaining_requests = int(response.headers["x-ratelimit-remaining"])
            
            if obj:
                if i > 0: print(")")
                return Food(obj)
                
        return Food(obj)


    def foods(self,
              fdcIds: list,
              format: Format=Format.abridged,
              nutrients: list=None):
        
        assert len(fdcIds) < 20, "Maximum number of foods for this endpoint is 20."

        if self.remaining_requests < 10:
                time.sleep(self.interval)
        """Retrieves a list of food items by a list of up to 20 FDC IDs.
        Optional format and nutrients can be specified. Invalid FDC ID's or ones
        that are not found are omitted and an empty set is returned if there are
        no matches.
            Endpoint: /foods
            Spec: https://fdc.nal.usda.gov/fdc_api.html#/FDC/postFoods
        """
        data = self.process_args(**{
            'fdcIds': fdcIds,
            'format': format,
            'nutrients': nutrients
        })

        response = self.api_post(data, "/foods")
        obj = json.loads(response.text) if response.status_code == 200 else None

        self.remaining_requests = int(response.headers["x-ratelimit-remaining"])
        
        return [Food(f) for f in obj]

    def foods_list(self,
                   dataTypes:list=[DataType.Foundation, DataType.SR, DataType.FNDDS],
                   pageSize:int=50,
                   pageNumber:int=1,
                   sortBy:Sorting=Sorting.dataType,
                   reverse=False):
        """Retrieves a paged list of foods. Use the pageNumber parameter to page
        through the entire result set.
            Endpoint: /foods/list
            Spec: https://fdc.nal.usda.gov/fdc_api.html#/FDC/postFoodsList
        """
        data = self.process_args(**{
            'dataTypes': dataTypes,
            'pageSize': pageSize,
            'pageNumber': pageNumber,
            'sortBy': sortBy,
            'reverse': reverse
        })
        response = requests.post(
            BASE_URL + '/foods/list',
            params={'api_key': self.api_key},
            json=data
        )
        obj = json.loads(response.text) if response.status_code == 200 else None
        return response, obj

    def api_get(self, endpoint):
        """ send GET to API using standard configuration"""
        headers = {'Content-Type': 'application/json'}

        url = BASE_URL + endpoint + "?api_key=" + self.api_key

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            if "Null key" not in response.text:
                print("WARNING: response code %s" % response.status_code)
                print(response.text)

        return response    

    def api_post(self, data, endpoint):
        """ send POST to API using standard configuration"""
        headers = {'Content-Type': 'application/json'}
        
        url = BASE_URL + endpoint + "?api_key=" + self.api_key

        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )

        if response.status_code != 200:
            print("WARNING: response code %s" % response.status_code)
            print(response.text)

        return response
    
    def foods_search(self,
                     query: str,
                     dataTypes:list=[DataType.Foundation, DataType.SR, DataType.FNDDS],
                     pageSize:int=10,
                     pageNumber:int=1,
                     sortBy:Sorting=Sorting.score,
                     reverse=False,
                     brandOwner:str=None, 
                     getAll=False,
                     exact=False):
        """Search for foods using keywords. Results can be filtered by dataType
        and there are options for result page sizes or sorting.
            Endpoint: /foods/search
            Spec: https://fdc.nal.usda.gov/fdc_api.html#/FDC/postFoodsSearch
        """
        data = self.process_args(**{
            'query': query,
            'dataTypes': dataTypes,
            'pageSize': pageSize,
            'pageNumber': pageNumber,
            'sortBy': sortBy,
            'reverse': reverse,
            'brandOwner': brandOwner
        })
        # dataType = data['dataType']
        # del data['dataType']
        # _json = {**data, 'dataType': dataType}

        if exact: 
            getAll = True
            pageSize = 200
            data['pageSize'] = pageSize

        # pprint.pprint(data)
        response = self.api_post(data, "/foods/search")

        obj = json.loads(response.text) if response.status_code == 200 else None
        if len(obj["foods"]) == 0:
            print("WARNING: nothing found for query {%s}" % query)

        if obj["totalPages"] > 1:
            if getAll:
                print("load all pages of %s" % obj["totalPages"])
                page_data = copy.copy(data)
                page_data['getAll'] = False
                page_data['exactMatch'] = False

                for i in range(2, obj["totalPages"]+1):
                    page_data['pageNumber'] = i
                    response = self.api_post(page_data, "/foods/search")
                    next_page_obj = json.loads(response.text) if response.status_code == 200 else None

                    # pprint.pprint(next_page_obj.keys())
                    del(next_page_obj["currentPage"])
                    del(next_page_obj["foodSearchCriteria"])

                    obj = mergedicts(obj, next_page_obj)

        assert obj is not None, "obj is unexpectedly None"

        if exact:
            obj['foods'] = [f for f in obj["foods"] if query.lower() in f["description"].lower()]

        return [{'description': data['description'], 'fdcId': data['fdcId']} for data in obj['foods']]

    def pretty_print_results(self, foods):
        # dict_keys(['fdcId', 'description', 'dataType',
        # 'gtinUpc', 'publishedDate', 'brandOwner', 'ingredients', 'foodNutrients', 'allHighlightFields', 'score'])

        for f in foods:
            print(f['description'] + " / " + f['dataType'] + " / " + str(f['fdcId']))

if __name__ == '__main__':
    client = Client("RcG9nFfxeyOhb94Vb3qktieFe07ulYbJwdh6kOj2")

    search_key = "coconut milk"
    search_results = client.foods_search(search_key, exact=True)
    print(search_results)

    # # food endpoint test
    # food = client.food(169228)
    # print(food)

    # # foods endpoint test
    # foods = client.foods([169228, 2346411])
    # print(foods)