from pymongo import MongoClient
import jsonpickle
import service.embedderService as embedder
import pandas as pd
import numpy as np


client = MongoClient('localhost', 27017)
db = client['emealio_food_db']
collection = db['ingredients']

def get_ingredient_by_name(ingredientName):
    ingredient = collection.find_one({"ingredient": ingredientName})
    return jsonpickle.encode(ingredient)

def get_most_similar_ingredient(ingredientName):
    ingredient = collection.find()
    ingredient_list = list(ingredient)
    #embed ingredientName
    ingredientNameEmbedding = embedder.embed_sentence(ingredientName)
    #convert ingredient to a pandas dataframe
    ingredient_df = pd.DataFrame(ingredient_list)
    #compute the similarity between the ingredientName and the ingredients in the database
    ingredient_df['similarity'] = ingredient_df.apply(lambda row: np.dot(row['ingredient_embedding'], ingredientNameEmbedding)/(np.linalg.norm(row['ingredient_embedding'])*np.linalg.norm(ingredientNameEmbedding)), axis=1)
    #sort the ingredients by similarity
    ingredient_df = ingredient_df.sort_values(by='similarity', ascending=False)
    top_ingredient_name = ingredient_df.head(1)["ingredient"].values[0]
    #get the top ingredient from the ingredient_list
    top_ingredient = next(item for item in ingredient_list if item["ingredient"] == top_ingredient_name)


    #convert the ingredient to a plain json
    return jsonpickle.encode(top_ingredient)