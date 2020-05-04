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

    def find_organic_select(self, foods, query):

        # if already 1 match found
        if isinstance(foods, dict):
            return foods
        if len(foods) == 1:
            return foods[0]

        # build a list of candidates to maximize data richness for nutrients
        candidates = []

        for f in foods:  # step 1a/1b
            query1 = query.lower()
            description = f['description'].lower()
            matches = [query1, query1 + ", raw", query1 + ", raw, nfs", query1 + ", nfs", query1 + ", fresh"]

            if description in matches or ("organic" and query in description):
                candidates.append(f)

        if len(candidates) == 1:
            print("exact match.")
            return candidates[0]

        if len(candidates) > 1:
            print("found %s candidates, show description, data type, count of nutrients, count of ingredients", len(candidates))
            for c in candidates:
                try:
                    print("%s | %s | %s | %s | %s" % (c["description"], c["dataType"], len(c["foodNutrients"]), len(c["ingredients"].split(",")), c["fdcId"]))
                except Exception:

                    print("%s | %s | %s | %s" % (c["description"], c["dataType"], len(c["foodNutrients"]), c["fdcId"]))

            # select candidate with max count of nutrients
            search_result = candidates[0]
            max_nutrients = len(search_result["foodNutrients"])
            for c in candidates:
                nutrients_count = len(c["foodNutrients"])
                if nutrients_count > max_nutrients:
                    max_nutrients = nutrients_count
                    search_result = c

            return search_result

    def find_organic(self, query, getAll=False):
        """ find organic foods"""

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


        result = self.find_organic_select(obj1['foods'], query)
        if result is not None:
            return result

        # search Branded foods
        response2, obj2 = self.client.foods_search(q, pageSize=200, dataTypes=[DataType.Branded], getAll=getAll)
        if len(obj2['foods']) == 0:
            raise Exception("nothing found for %s" % query)

        result = self.find_organic_select(obj2['foods'], query)

        if result is not None:
            return result
        print("=== NO SATISFYING MATCH FOUND :-[] ===")
        print("== non-branded foods ==")
        self.client.pretty_print_results(obj1["foods"])
        print("== branded foods ==")
        self.client.pretty_print_results(obj2["foods"])
        raise Exception("nothing found for %s" % query)


    def remove_punctuations(self, str):
        # https://www.programiz.com/python-programming/examples/remove-punctuation
        # define punctuation
        punctuations = '''!()-[]{};:'"\\<>./?@#$%^&*_~'''
        no_punct = ""
        for char in str:
            if char not in punctuations:
                no_punct = no_punct + char

        return no_punct
