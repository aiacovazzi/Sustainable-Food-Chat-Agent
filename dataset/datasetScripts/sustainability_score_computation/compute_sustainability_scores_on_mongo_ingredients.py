
from pymongo import MongoClient
import numpy as np
import pandas as pd
#connect to mongodb
client = MongoClient('localhost', 27017)
db = client['emealio_food_db']
collection = db['ingredients']

#Normalize the values of the cfp and wfp
def normalize_cfp_wfp():
    #query for selecting all the ingredients that have a cfp value not null
    cfp_not_null = collection.find({"cfp": {"$ne": None}})

    cfp_not_null_values = cfp_not_null.distinct('cfp')

    cfp_max = max(cfp_not_null_values)
    cfp_min = min(cfp_not_null_values)

    #query for selecting all the ingredients that have a wfp value not null
    wfp_not_null = collection.find({"wfp": {"$ne": None}})

    wfp_not_null_values = wfp_not_null.distinct('wfp')

    wfp_max = max(wfp_not_null_values)
    wfp_min = min(wfp_not_null_values)

    #print values
    print("CFP max: ", cfp_max)
    print("CFP min: ", cfp_min)

    print("WFP max: ", wfp_max)
    print("WFP min: ", wfp_min)

    #loop through the ingredients and normalize the values (cfp and wfp could not exist for some ingredients, check if they exist)
    #add the normalized values to the database usign the fields cfp_normalized and wfp_normalized

    for ingredient in collection.find():
        if 'cfp' in ingredient and ingredient['cfp'] is not None:
            cfp_normalized = (ingredient['cfp'] - cfp_min) / (cfp_max - cfp_min)
            collection.update_one({"_id": ingredient['_id']}, {"$set": {"cfp_normalized": cfp_normalized}})
        if 'wfp' in ingredient and ingredient['wfp'] is not None:
            wfp_normalized = (ingredient['wfp'] - wfp_min) / (wfp_max - wfp_min)
            collection.update_one({"_id": ingredient['_id']}, {"$set": {"wfp_normalized": wfp_normalized}})

    print("Normalization done")

normalize_cfp_wfp()