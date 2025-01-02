from pymongo import MongoClient
import service.embedderService as embedder
import pandas as pd
import jsonpickle
import numpy as np

client = MongoClient('localhost', 27017)
db = client['emealio_food_db']
collection = db['recipes']
recipe_list = None

#treat the recipe list as a singleton in order to avoid to load it every time
def get_recipe_list():
    global recipe_list
    if recipe_list is None:
        recipe_list = list(collection.find())
    return recipe_list

def get_recipe_by_id(recipeId):
    recipe = collection.find_one({"id": recipeId})
    return jsonpickle.encode(recipe)

def get_recipe_by_title(recipeTitle):
    query = """{"title": { "$regex": "RECIPE_TITLE", "$options": "i" }}"""
    query = query.replace('RECIPE_TITLE',recipeTitle)
    query = jsonpickle.decode(query)
    recipe = collection.find(query)
    found = list(recipe)
    found.sort(key=lambda x: len(x["title"]))
    first = found[0]
    return jsonpickle.encode(first)

def get_most_similar_recipe(recipeTitle):

    recipe_list = get_recipe_list()
    #embed recipeTitle
    recipeTitleEmbedding = embedder.embed_sentence(recipeTitle)
    #convert recipe to a pandas dataframe
    recipe_df = pd.DataFrame(recipe_list)
    #compute the similarity between the recipeTitle and the recipes in the database
    recipe_df['similarity'] = recipe_df.apply(lambda row: np.dot(row['title_embedding'], recipeTitleEmbedding)/(np.linalg.norm(row['title_embedding'])*np.linalg.norm(recipeTitleEmbedding)), axis=1)
    #sort the recipes by similarity
    recipe_df = recipe_df.sort_values(by='similarity', ascending=False)
    top_recipe_title = recipe_df.head(1)["title"].values[0]
    #get the top recipe from the recipe_list
    top_recipe = next(item for item in recipe_list if item["title"] == top_recipe_title)

    #convert the recipe to a plain json
    return jsonpickle.encode(top_recipe)