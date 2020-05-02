import pprint
from noms.client.client2 import DataType


class Foods:
    def __init__(self, client):
        self.client = client

    def exact_match(self, query):
        """ return items matching exact description """
        query = "description:" + query
        response, obj = self.client.foods_search(query, pageSize=200)
        assert obj is not None
        result = []

        # pprint.pprint(obj.keys())
        pagesCount = obj["totalPages"]
        if pagesCount > 1:
            print("WARNING: total pages count is %s" % pagesCount)

        for item in obj["foods"]:
            pprint.pprint(item)
            if item["description"].lower() == query:
                result.append(item)

        return result, obj['foods']

    def is_organic(self, item):
        """ do heuristics to estimate whether product is organic food """
        result = False

        description = self.remove_punctuations(item["description"]).lower().strip()
        ingredients = self.remove_punctuations(item["ingredients"]).lower().strip()

        if ingredients == "organic " + description:
            result = True

        if description == ingredients:
            result = True

        if ingredients == "":
            result = True

        if result is False:
            print("skip as non-organic: %s -> %s", (item["description"], item["ingredients"]))

        return result

    def find_organic(self, query, getAll=False):
        """ do exact search and match keyword organic in ingredients"""

        # search strategy: for cooking, get exactly one reference product. Later on maybe need to compute an average abstract product.
        # step 0: if exactly one match, this might be non-organic, but consider so far to be a special case
        # step 1: search for description match, all DB but Branded type
        # step 1a: check if exact match available
        # step 1b: if no exact match, look if there is a ", raw" etc. addon in same results
        # step 2: search on Branded type
        q = "description:" + query
        filter = [DataType.Foundation, DataType.SR, DataType.FNDDS]
        response1, obj1 = self.client.foods_search(q, pageSize=200, dataTypes=filter, getAll=getAll)
        if len(obj1['foods']) == 0:
            raise Exception("nothing found for %s" % query)

        # if already 1 match found
        if isinstance(obj1['foods'], dict):
            return obj1['foods']
        if len(obj1['foods']) == 1:
            return obj1['foods'][0]

        for f in obj1['foods']:  # step 1a/1b
            description = f['description'].lower()
            matches = [query, query + ", raw", query + ", raw, nfs", query + ", nfs", query + ", fresh"]

            if description in matches:
                return f

        # search Branded foods
        response2, obj2 = self.client.foods_search(q, pageSize=200, dataTypes=[DataType.Branded], getAll=getAll)
        if len(obj1['foods']) == 0:
            raise Exception("nothing found for %s" % query)

        # if already 1 match found
        if isinstance(obj2['foods'], dict):
            return obj2['foods']
        if  len(obj2['foods']) == 1:
            return obj2['foods'][0]

        for f in obj2['foods']:  # step 1a/1b
            description = f['description'].lower()
            matches = [query, query + ", raw", query + ", fresh"]
            if description in matches:
                return f

        print("=== NO SATISFYING MATCH FOUND :-[] ===")
        print("== non-branded foods ==")
        self.client.pretty_print_results(obj1["foods"])
        print("== branded foods ==")
        raise Exception("nothing found for %s" % query)
        #
        # response2, obj2 = self.client.foods_search(query+", raw", pageSize=200)
        # assert obj2 is not None
        #
        # foods = obj1['foods'] + obj2['foods']
        #
        # result = []
        #
        # # pprint.pprint(obj.keys())
        # pagesCount = obj1["totalPages"]
        # if pagesCount > 1:
        #     print("WARNING: total pages count is %s" % pagesCount)
        #
        # for item in foods:
        #     if item["description"].lower() == query and self.is_organic(item):
        #         result.append(item)
        #     else:
        #         print("skip %s" % (item['description']))
        #
        return obj1['foods']

    def remove_punctuations(self, str):
        # https://www.programiz.com/python-programming/examples/remove-punctuation
        # define punctuation
        punctuations = '''!()-[]{};:'"\\<>./?@#$%^&*_~'''
        no_punct = ""
        for char in str:
            if char not in punctuations:
                no_punct = no_punct + char

        return no_punct
