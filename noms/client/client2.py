"""Client class to interface with FoodData Central.
FoodData Central requires a Data.gov key: https://api.data.gov/signup/
"""

from enum import Enum
import json
import time
import requests

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


class Client2:
    def __init__(self, api_key):
        self.api_key = api_key

        self.interval = 1  # current API does not allow over 1 request/second.

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
             fdcId: str,
             format: Format=Format.abridged,
             nutrients: list=None):

        time.sleep(self.interval)
        """Retrieves a single food item by an FDC ID. Optional format and
        nutrients can be specified.
            Endpoint: /food/{fdcId}
            Spec: https://fdc.nal.usda.gov/fdc_api.html#/FDC/getFood
        """
        data = self.process_args(**{
            'format': format,
            'nutrients': nutrients
        })

        response = self.api_post(data)

        obj = json.loads(response.text) if response.status_code == 200 else None
        return response, obj


    def foods(self,
              fdcIds: list,
              format: Format=Format.abridged,
              nutrients: list=None):

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

        response = self.api_post(data)
        obj = json.loads(response.text) if response.status_code == 200 else None
        return response, obj

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

    def api_post(self, data):
        """ send POST to API using standard configuration"""
        headers = {'Content-Type': 'application/json'}

        # pprint.pprint(data)
        # sys.exit(0)

        response = requests.post(
            BASE_URL + '/foods/search/?api_key='+self.api_key,
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
                     pageSize:int=50,
                     pageNumber:int=1,
                     sortBy:Sorting=Sorting.dataType,
                     reverse=False,
                     brandOwner:str=None, getAll=False):
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

        # pprint.pprint(data)
        response = self.api_post(data)

        obj = json.loads(response.text) if response.status_code == 200 else None
        if len(obj["foods"]) == 0:
            print("WARNING: nothing found for query {%s}" % query)

        if obj["totalPages"] > 1:
            if getAll:
                print("load all pages of %s" % obj["totalPages"])
                for i in range(2, obj["totalPages"]+1):
                    response, next_page_obj = self.foods_search(query=query,
                                      dataTypes=dataTypes,
                                      pageSize=pageSize,
                                      pageNumber=i,
                                      sortBy=sortBy,
                                      reverse=reverse,
                                      brandOwner=brandOwner,
                                      getAll=False)
                    # pprint.pprint(next_page_obj.keys())
                    del(next_page_obj["currentPage"])
                    del(next_page_obj["foodSearchCriteria"])

                    obj = mergedicts(obj, next_page_obj)

        assert obj is not None, "obj is unexpectedly None"
        return response, obj

    def pretty_print_results(self, foods):
        # dict_keys(['fdcId', 'description', 'dataType',
        # 'gtinUpc', 'publishedDate', 'brandOwner', 'ingredients', 'foodNutrients', 'allHighlightFields', 'score'])

        for f in foods:
            print(f['description'] + " / " + f['dataType'] + " / " + str(f['fdcId']))
