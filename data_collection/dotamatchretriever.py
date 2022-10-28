import graphene
import os
import json
import requests
from dota2py import api
from pymongo import MongoClient
from time import sleep
from stratz_api import query_stratz_api

def initialize_apis():
    VALVE_API_KEY = os.getenv('VALVE_DOTA2_API_KEY')
    if not VALVE_API_KEY:
        raise NameError('No "VALVE_DOTA2_API_KEY" found in the system environment')
    api.set_api_key(VALVE_API_KEY)

def initialize_database():
    CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
    if not CONNECTION_STRING:
        raise NameError('No "COSMOS_CONNECTION_STRING" found in the system environment')\

    return MongoClient(CONNECTION_STRING)

def check_validity(match_id):
    match_results = api.get_match_details(match_id)['result']
    for player in match_results['players']:
        if player['leaver_status'] != 0:
            return False
    return True

def sort_role_information(player_info):
    dire_team = []
    radiant_team = []
    for player in player_info:
        if player['isRadiant']:
            radiant_team.append(player)
        else:
            dire_team.append(player)

    # need to handle junglers last as it could refer to carry or offlane
    radiant_junglers = []
    for player in radiant_team:
        if player['lane'] == 'JUNGLE':
            radiant_team.remove(player)
            radiant_junglers.append(player)
    if(len(radiant_junglers) > 1):
        return # returns if more than 1 jungler bc unabled to tell which is which role and it is not normal behaviour to have 2 junglers

    dire_junglers = []
    for player in dire_team:
        if player['lane'] == 'JUNGLE':
            if player['role'] == 'CORE':
                dire_team.remove(player)
                dire_junglers.append(player)
    if(len(dire_junglers) > 1):
        return # returns if more than 1 jungler bc unabled to tell which is which role and it is not normal behaviour to have 2 junglers

    sorted_heroes = {}
    for player in radiant_team:
        if player['role'] == 'CORE':
            if player['lane'] == 'OFF_LANE':
                sorted_heroes['radiant_offlaner'] = player['heroId']
            elif player['lane'] == 'MID_LANE':
                sorted_heroes['radiant_mid'] = player['heroId']
            elif player['lane'] == 'SAFE_LANE':
                sorted_heroes['radiant_carry'] = player['heroId']
        elif player['role'] == 'LIGHT_SUPPORT' or player['role'] == 'HARD_SUPPORT':
            if player['lane'] == 'SAFE_LANE':
                sorted_heroes['radiant_hard_support'] = player['heroId']
            elif player['lane'] == 'OFF_LANE' or player['lane'] == 'JUNGLE':
                if 'radiant_soft_support' in sorted_heroes.keys():
                    sorted_heroes['radiant_hard_support'] = player['heroId']
                else:
                    sorted_heroes['radiant_soft_support'] = player['heroId']

    if(len(radiant_junglers) > 0):
        if 'radiant_carry' in sorted_heroes.keys():
            sorted_heroes['radiant_offlaner'] = radiant_junglers[0]['heroId']
        else:
            sorted_heroes['radiant_carry'] = radiant_junglers[0]['heroId']

    for player in dire_team:
        if player['role'] == 'CORE':
            if player['lane'] == 'OFF_LANE':
                sorted_heroes['dire_offlaner'] = player['heroId']
            elif player['lane'] == 'MID_LANE':
                sorted_heroes['dire_mid'] = player['heroId']
            elif player['lane'] == 'SAFE_LANE':
                sorted_heroes['dire_carry'] = player['heroId']
        elif player['role'] == 'LIGHT_SUPPORT' or player['role'] == 'HARD_SUPPORT':
            if player['lane'] == 'SAFE_LANE':
                sorted_heroes['dire_hard_support'] = player['heroId']
            elif player['lane'] == 'OFF_LANE' or player['lane'] == 'JUNGLE':
                if 'dire_soft_support' in sorted_heroes.keys():
                    sorted_heroes['dire_hard_support'] = player['heroId']
                else:
                    sorted_heroes['dire_soft_support'] = player['heroId']

    if(len(dire_junglers) > 0):
        if 'dire_carry' in sorted_heroes.keys():
            sorted_heroes['dire_offlaner'] = dire_junglers[0]['heroId']
        else:
            sorted_heroes['dire_carry'] = dire_junglers[0]['heroId']

    return sorted_heroes

def process_match_data(parsed_matches, match_database):
    matches = parsed_matches['matches']
    for match in matches:
        #print(match)
        example = {}
        example['match_id'] =match['id']
        example['did_radiant_win'] = int(match['didRadiantWin'])

        sorted_role_information = sort_role_information(match['players'])

        if not sorted_role_information:
            continue

        try:
            example['radiant_offlaner'] = sorted_role_information['radiant_offlaner']
            example['radiant_mid'] = sorted_role_information['radiant_mid']
            example['radiant_carry'] = sorted_role_information['radiant_carry']
            example['radiant_soft_support'] = sorted_role_information['radiant_soft_support']
            example['radiant_hard_support'] = sorted_role_information['radiant_hard_support']

            example['dire_offlaner'] = sorted_role_information['dire_offlaner']
            example['dire_mid'] = sorted_role_information['dire_mid']
            example['dire_carry'] = sorted_role_information['dire_carry']
            example['dire_soft_support'] = sorted_role_information['dire_soft_support']
            example['dire_hard_support'] = sorted_role_information['dire_hard_support']

        except(KeyError):
            print("invalid role information")
            continue

        print("Inserting " + str(match['id']) + " to the database")
        match_database.insert_one(example)


def get_replay_parse_info(valid_match_ids, match_database):
    while(len(valid_match_ids) > 0):
        if(len(valid_match_ids) < 10):
            current_subset_ids = valid_match_ids
            break
        else:
            current_subset_ids = valid_match_ids[:10]
            valid_match_ids = valid_match_ids[10:len(valid_match_ids)-1]
        sleep(1)
        parsed_matches = query_stratz_api(current_subset_ids)
        process_match_data(parsed_matches, match_database)


def main(match_database):
    start_match_id = None
    valid_match_ids = []
    while(True):
        sleep(2)
        try:
            match_history = api.get_match_history(start_at_match_id=start_match_id, skill=3, game_mode=2, min_players=10)['result']
        except(requests.exceptions.HTTPError):
            print("Steam API Timedout")
            break
        matches = match_history['matches']

        if(len(matches) == 0):
            break

        for match in matches:
            match_id = match['match_id']
            if match_database.find_one({'match_id': match_id}) != None:
                break
            sleep(2)
            if not check_validity(match_id):
                continue
            valid_match_ids.append(match_id)

        last_match_id = matches[-1]['match_id']
        start_match_id = last_match_id

    # needs to sleep of 5 mins to allow for stratz to parse replay in order to obtain relavent information
    print("parsing matches now")
    sleep(300)
    get_replay_parse_info(valid_match_ids, match_database)

if __name__ == '__main__':
    initialize_apis()
    client = initialize_database()

    db = client['seng-474']
    matches = db.match_data
    while(True):
        print("Number of examples in databse: " + str(matches.count_documents({})))
        try:
            main(matches)
        except(requests.exceptions.HTTPError):
            print("HTTPError Sleeping for 1 Hour")
        sleep(7200)
