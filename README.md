# Nutrient Object Management System (noms)

noms is a fun and simple Python package that allows you to obtain and work with highly detailed nutrition data for nearly 8,000 entries from the USDA Standard Reference Food Composition Database. No mainstream nutrition tracker apps reflect the level of detail that the USDA has compiled. With noms you can track:

1. Proximates including macronutrients (protein, carbs, and fat), calories, fiber and water content
2. 11 minerals
3. 13 vitamins
4. Specific lipids including EPA and DHA (the most important omega-3s found in fish oil)

This amounts to 41 nutrients being tracked, but many more are available from the database such as amino acids and other lipids. These can be viewed in all_nutrient_ids.txt, and support for other nutrients will be added in the future as requested. You can add support for these yourself by editing noms/objects/nutrient_ids.json accordingly with entries from all_nutrient_ids.txt.

Note: The Standard Reference Database is used explicitly without the addition of the USDA's Branded Foods database, as only the former allows for highly detailed reports which track 168 different nutrients -- much more information than you would find on an item's nutrition facts! This is especially valuable for nutritionists or people interested in their own health to explore the nutritional content of whole foods.

## Installation

This version of the noms package is not listed and must be cloned:

```bash
git clone git@github.com:patrickwalton/noms.git
```

Then, you can install using pip:

```bash
pip install noms
```

## Getting Started

1. Get a data.gov API key for free from [here](https://api.data.gov/signup/).
2. Initialize a client object with the key you received.

```python
import noms
client = noms.Client("api key")
```

## Searching the Database

```python
search_results = client.foods_search("Raw Broccoli")
pprint.pprint(search_results)
```

```output
[('Eggplant, raw', 169228),
 ('Eggplant, raw', 2345305),
 ('Eggplant dip', 2345576),
 ('Eggplant, pickled', 169892),
 ('Eggplant, pickled', 2345608),
 ('Fried eggplant', 2345575),
 ('Eggplant and meat casserole', 2345693),
 ('Eggplant, cooked, as ingredient', 2346375),
 ('Eggplant with cheese and tomato sauce', 2345578),
 ('Eggplant parmesan casserole, regular', 2345577)]
```

## Requesting Foods by ID

You can request a single or multiple foods by ID.

### Requesting a Single Food

Use noms.Client.food() to get a single food by ID. For example, the ID for raw eggplant is: 169228.

```python
food_list = client.food(169228)
```

This returns a noms.Food object.

### Requesting Multiple Foods

Use noms.Client.foods() to get a single food by ID. For this example, we use raw blueberries (ID = 2346411) as an additional food.

```python
food_list = client.foods([169228, 2346411)
```

This returns a list of noms.Food objects.

## Urgent Work to be Done

- [x] Re-implement search by ID.
- [x] Immediately convert API results for search_by_id to a cleaner object.
- [x] Trim search by name to only give names and IDs for later use in search by ID.
- [x] Fix the foods_search pretty print.
- [ ] Implement [smarter rate limiting](https://api.data.gov/docs/rate-limits/) and daily rate limiting for demo key.
- [ ] Figure out if we can step through page results on the search.

## Someday Work to be Done

- [ ] Make it easier to specify only foundation or other data types.
- [ ] Add capability to specify amount of each food in API lookup or after.
- [ ] Convert nutrition facts to food attributes?
- [ ] Add examples folder. Use [DEMO_KEY](https://fdc.nal.usda.gov/api-guide.html) in examples.
- [ ] Decide how to scope this project. Maybe it's best to leave it as an API wrapper and build the rest of my work as part of the meals app backend. That way, the API wrapper is easy to maintain and would be fun to share.
- [ ] Add support for downloading the database if someone wants to get over the rate limit. Better to do this only if the rate limit is causing problems, because doing so requires the data be periodically updated. This would help with exact search too.
- [ ] Rename to match USDA API name and publish to pypi!
- [ ] Flush out other properties.
