import bson
import pandas as pd
import json

def name_lookup(id):
    with open("data_collection/heroes.json", 'r') as json_file:
        hero_name_lookup_table = json.load(json_file)
        return hero_name_lookup_table[str(id)]

match_list = []

labels = ['radiant_1', 'radiant_2', 'radiant_3', 'radiant_4', 'radiant_5', 'dire_1', 'dire_2', 'dire_3', 'dire_4', 'dire_5']

with open('data_collection/matches.bson', 'rb') as matches:
    document = matches.read()
    base = 0
    count = 0
    while base < len(document):
        match_dic = {}
        base, d = bson.decode_document(document, base)
        if(d['human_players'] != 10):
            continue
        if(d['game_mode'] != 1):
            continue

        match_dic['match_id'] = d['match_id']
        if(d['radiant_win'] == True):
            match_dic['did_radiant_win'] = 1
        else:
            match_dic['did_radiant_win'] = 0
        for i, player in enumerate(d['players']):
            match_dic[labels[i]] = name_lookup(player['hero_id'])
        count += 1
        print(count)
        match_list.append(match_dic)

df = pd.json_normalize(match_list)
df.to_csv('prediction_model/old_data.csv', index=False)
