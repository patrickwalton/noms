class SearchResults():
    """
    An object returned by Client.search_query which stores a Python dictionary
    containing all of the search result information.
    """
    def __init__(self, json):
        self.json = json
    def __str__(self, max_entries=None):
        r_str = ""
        if self.json == None:
            r_str += "There are no search results for this query\n"
        else:
            r_str +="="*112 + "\n"
            r_str +="Search results for \'{}\' on USDA Standard Reference Database".format(self.json["search_term"]) + "\n"
            r_str +="="*112 + "\n"
            if max_entries == None:
                max_entries = len(self.json["items"])
            if max_entries < len(self.json["items"]):
                self.json["items"] = self.json["items"][:max_entries]
            self.json["items"].sort(key=operator.itemgetter("group"))
            r_str +="{name:<72} {group:^30} {id:>8}".format(name="Name",group="Group",id="ID") + "\n"
            for item in self.json["items"]:
                if len(item["name"]) > 70:
                    item["name"] = item["name"][:70] + ".."
                if len(item["group"]) > 28:
                    item["group"] = item["group"][:28] + ".."
                r_str +="{name:<72} {group:^30} {id:>8}".format(name=item["name"],group=item["group"],id=item["ndbno"]) + "\n"
            r_str +="="*112 + "\n"
        return r_str
