
import json

from requests_debugger import requests
#import requests
from noms.client.dict_parse import search_parse
from noms.client.dict_parse import food_parse
from noms.client.searchresults import SearchResults
from noms.objects.nutrient_dict import *
import pprint

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


    def call_post(self, params, url_suffix):
        """ target_url could be:
        https://api.nal.usda.gov/usda/ndb/V2/reports
        https://api.nal.usda.gov/usda/ndb/search
        depending on which service of the api is being used
        """
        target_url = self.url + url_suffix
        params["api_key"] = self.key
        response = json.loads(requests.post(url=target_url, params=params).text)
        if 'error' in response.keys() and response['status'] is not 200:
            raise Exception(response)
        return response

    def call(self, params, url_suffix):
        """ target_url could be:
        https://api.nal.usda.gov/usda/ndb/V2/reports
        https://api.nal.usda.gov/usda/ndb/search
        depending on which service of the api is being used
        """
        target_url = self.url + url_suffix
        params["api_key"] = self.key
        response = json.loads(requests.get(url=target_url, params=params).text)

        # seems like normal API operation
        if type(response) == list:
            return {'foods': response}

        # if nothing found there is None type
        if response is None:
            return {'foods': []}

        # error handling: return type dict with error details
        if 'error' in response.keys() and response['status'] != 200:
            raise Exception(response)

    def search_query(self, query, dataType=None):
        params = dict(
            query=query
        )
        #result = search_parse(self.call(params,'/foods/search'))
        #pprint.pprint(result['items'])
        return SearchResults(search_parse(self.call(params, '/foods/search')))

    def food_query(self, ids):
        # allow for either a single id (ndbno) query, or a list of queries
        if type(ids) == list:
            if len(ids) > 25:
                raise Exception("Too many Food ID arguments. API limits it to 25.")
        params = dict(fdcIds=ids)
        # params.update(dict(type='f', format='json'))
        return_obj = self.call(params, '/foods')
        offset = 0
        return return_obj
        if 'foods' not in return_obj:
            raise Exception("No 'foods' index.\nSee the following error: {}".format(return_obj))
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
