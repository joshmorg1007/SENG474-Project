import os
import sklearn
from pymongo import MongoClient
import pandas as pd
import json

def map_series_to_names(series):
    new_series = series.apply(map_ids_to_names)
    return new_series

def map_ids_to_names(id):
    with open("prediction_model/heroes.json", 'r') as json_file:
        hero_name_lookup_table = json.load(json_file)
        return hero_name_lookup_table[str(id)]

def main():
    with open("prediction_model/connection_string.txt") as file:
        connection_string = file.read()

        client = MongoClient(connection_string)
        db = client['seng-474']
        matches = db.match_data

        print(matches.count_documents({}))

        curser = matches.find({})

        df = pd.DataFrame(list(curser))
        print(len(df))

        df[['radiant_offlaner', 'radiant_mid', 'radiant_carry', 'radiant_soft_support', 'radiant_hard_support',
                'dire_offlaner', 'dire_mid', 'dire_carry', 'dire_soft_support', 'dire_hard_support']] = df[['radiant_offlaner', 'radiant_mid', 'radiant_carry', 'radiant_soft_support', 'radiant_hard_support',
                'dire_offlaner', 'dire_mid', 'dire_carry', 'dire_soft_support', 'dire_hard_support']].apply(map_series_to_names)


        print(df.head())
        df.to_csv("prediction_model/data.csv", index=False)

if __name__ == '__main__':
    main()
