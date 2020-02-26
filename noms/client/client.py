
import json

from requests_debugger import requests
#import requests
from noms.client.dict_parse import search_parse
from noms.client.dict_parse import food_parse
from noms.client.searchresults import SearchResults
from noms.objects.nutrient_dict import *

class Client:
    """
    The Client class is used to interface with the USDA Standard Reference Database
    API. It must be initialized with an API key.
    """

    url = 'https://api.nal.usda.gov/usda/ndb'
    url = 'https://api.nal.usda.gov/fdc/v1'



    def __init__(self, key):
        """
        A Client instance must be initialized with a key from
        data.gov. This is free to obtain, and you can request one
        here: https://api.data.gov/signup/
        """
        self.key = key.strip()

    def call(self, params, url_suffix):
        """ target_url could be:
        https://api.nal.usda.gov/usda/ndb/V2/reports
        https://api.nal.usda.gov/usda/ndb/search
        depending on which service of the api is being used
        """
        target_url = self.url + url_suffix
        # add the key to the API call
        print(self.key)
        call_params = dict(params, api_key=self.key)
        response = json.loads(requests.get(url=target_url, params=call_params).text)
        return response

    def search_query(self, name):
        params = dict(
            q=name,
            ds='Standard Reference',
            format='json'
        )
        result = search_parse(self.call(params,'/search'))
        if result == None:
            return None
        else:
            return SearchResults(search_parse(self.call(params, '/search')))

    def food_query(self, ids):
        # allow for either a single id (ndbno) query, or a list of queries
        if type(ids) == list:
            if len(ids) > 25:
                raise Exception("Too many Food ID arguments. API limits it to 25.")
        params = dict(ndbno=ids)
        params.update(dict(type='f', format='json'))
        return_obj = self.call(params, '/V2/reports')
        offset = 0
        if 'foods' not in return_obj:
            print("See the following error: {}".format(return_obj))
            return None
        for i in range(0, len(return_obj["foods"])):
            if 'error' in return_obj["foods"][i-offset].keys():
                del return_obj["foods"][i-offset]
                offset += 1
        return return_obj

    def get_foods(self, id_value_dict):
        # If more than 25 words are being queried, split it up
        if len(id_value_dict.keys()) > 25:
            print("Must call the database {} times, this may take a couple moments. Status: {leng}/{leng}".format(len(id_value_dict.keys())//25+1,leng=len(id_value_dict.keys())))
            dict_copy = id_value_dict.copy()
            food_obj = []
            while len(dict_copy.keys()) > 25:
                current_dict = {}
                items = islice(dict_copy.items(), 25)
                current_dict.update(items)
                call = self.food_query(current_dict.keys())
                food_obj += food_parse(call, nutrient_dict, list(current_dict.values()))
                for key in current_dict.keys():
                    del dict_copy[key]
                print("Status: {}/{}".format(len(dict_copy.keys()), len(id_value_dict.keys())))
            call = self.food_query(dict_copy.keys())
            food_obj += food_parse(call, nutrient_dict, list(dict_copy.values()))
            print("Complete!")
        else:
            food_obj = self.food_query(id_value_dict.keys())
            food_obj = food_parse(food_obj, nutrient_dict, list(id_value_dict.values()))
        return food_obj
