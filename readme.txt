##### UVIC - SENG 474 2022 Project - Dota 2 Match Outcome Classifier Using Hero Selection #####

This repo contains the models and data collection scripts used in order to complete the project component of SENG 474 at the University of Victoria


##### Overview of the Repository #####
data_collection\
    convert_old_dataset.py -- script that takes the original .bson database file from the original paper and converts it to format that the jupyter notebook file
                              containing the model information can read
    dotamatchretreiver.py -- Main script uses the Valve API to get the most recent matches and calls the STRATZ API to parse the replay to extract aditional Role
                             information
    stratz_api.py -- helper script that contains the query structure for the STRATZ API
    strip_heroes_json.py -- Pulls the list of heroes from OpenDota github and creates a json map of hero id to localized name

Figures\ -- Various figures ommitted from the report in order to meet the 6 page requirement

prediction_model\
    data.csv -- current dataset gathered using dotamatchretreiver.py
    dota_draft_predictor.ipynb -- jupyter notebook file that contains all models trained (currently has output of data.csv)
    old_data.csv -- original dataset converted from bson file.
