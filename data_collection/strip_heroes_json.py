import requests
import json
response = requests.get("https://raw.githubusercontent.com/odota/dotaconstants/master/build/heroes.json")

hero_lookup = {}

for hero_id, details in response.json().items():
    hero_lookup[hero_id] = details['localized_name']

print(hero_lookup)

with open('data_collection/heroes.json', 'w') as output_file:
    json.dump(hero_lookup, output_file, indent=4)