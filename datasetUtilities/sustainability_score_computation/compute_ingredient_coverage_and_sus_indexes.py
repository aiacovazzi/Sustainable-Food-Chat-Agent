import pandas as pd
import math
import numpy as np
import sys
from pymongo import MongoClient

def remove_additional_info(ingredient):
    #given a string like "water _ 2 __ cups"
    #find the  index of the character "_" and remove everything after it
    index = ingredient.find(' _')
    #if the character is not found then return the string as it is
    if index != -1:
        #get the substring from 0 to the index minus 1
        ingredient = ingredient[:index]
    #remove [,],{,} and '
    ingredient = ingredient.replace('[','')
    ingredient = ingredient.replace(']','')
    ingredient = ingredient.replace('{','')
    ingredient = ingredient.replace('}','')
    ingredient = ingredient.replace('"','')
    ingredient = ingredient.replace('\'','')
    #remove trailing and leading spaces
    return ingredient

def get_ingredients(ingredients):
    ingredients = ingredients.split("',")
    ingredients = [ingredient.strip() for ingredient in ingredients]
    ingredients = [remove_additional_info(ingredient) for ingredient in ingredients]
    return ingredients

def count_covered_wfp(ingredients_connection, ingredient_list):
    covered = 0

    for i in ingredient_list:
        ingredient = ingredients_connection.find_one({'ingredient': i})
        if ingredient is not None:
            if 'wfp' in ingredient:
                wfp = ingredient['wfp']
                if not math.isnan(wfp):
                    covered += 1

    return covered

def count_covered_cfp(ingredients_connection, ingredient_list):
    covered = 0

    for i in ingredient_list:
        ingredient = ingredients_connection.find_one({'ingredient': i})
        if ingredient is not None:
            if 'cfp' in ingredient:
                cfp = ingredient['cfp']
                if not math.isnan(cfp):
                    covered += 1

    return covered

def compute_coverage():
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']
    ingredients_db = db['ingredients']
    recipes_cursor = recipes_db.find()

    #loop over the recipes
    for recipe in recipes_cursor:
        #get the ingredients
        ingredients = recipe['ingredients']
        ingredients_list = get_ingredients(ingredients)
        total_ingredients = len(ingredients_list)

        covered_cfp = count_covered_cfp(ingredients_db, ingredients_list)
        percentage_covered_cfp = (covered_cfp/total_ingredients)*100

        covered_wfp = count_covered_wfp(ingredients_db, ingredients_list)
        percentage_covered_wfp = (covered_wfp/total_ingredients)*100

        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"percentage_covered_cfp": percentage_covered_cfp}})
        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"percentage_covered_wfp": percentage_covered_wfp}})

    print("Done")

def compute_cfp_sustainability(ingredients_list, ingredients_db):
    cfps = []
    for ingredient in ingredients_list:
        ingredient = ingredients_db.find_one({'ingredient': ingredient})
        if ingredient is not None:
            if 'cfp_normalized' in ingredient:
                cfps.append(ingredient['cfp_normalized'])
    #order cfps in descending order
    cfps.sort(reverse=True)

    cfp_score = 0
    for i in range(len(cfps)):
        cfp_score += cfps[i] * math.e ** (-i)
    
    return cfp_score

def compute_wfp_sustainability(ingredients_list, ingredients_db):
    wfps = []
    for ingredient in ingredients_list:
        ingredient = ingredients_db.find_one({'ingredient': ingredient})
        if ingredient is not None:
            if 'wfp_normalized' in ingredient:
                wfps.append(ingredient['wfp_normalized'])
    #order wfps in descending order
    wfps.sort(reverse=True)

    wfp_score = 0
    for i in range(len(wfps)):
        wfp_score += wfps[i] * math.e ** (-i)

    return wfp_score

def compute_sustainability_scores():
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']
    ingredients_db = db['ingredients']
    recipes_cursor = recipes_db.find()

    for recipe in recipes_cursor:
        ingredients = recipe['ingredients']
        ingredients_list = get_ingredients(ingredients)

        cfp_score = compute_cfp_sustainability(ingredients_list, ingredients_db)
        wfp_score = compute_wfp_sustainability(ingredients_list, ingredients_db)

        print("Recipe: ", recipe['title'])

        #print("CFP: ", cfp_score)
        #print("WFP: ", wfp_score)

        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"cfp_sustainability": cfp_score}})
        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"wfp_sustainability": wfp_score}})

    print("Done")

def compute_overall_sustainability_scores():
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']
    recipes_cursor = recipes_db.find()
    alpha = 0.8
    beta = 0.2

    for recipe in recipes_cursor:
        cfp_sustainability = recipe['cfp_sustainability']
        wfp_sustainability = recipe['wfp_sustainability']

        print("Recipe: ", recipe['title'])

        overall_sustainability = alpha * cfp_sustainability + beta * wfp_sustainability
        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"overall_sustainability": overall_sustainability}})

    print("Done")

def compute_normalized_sustainability_scores():
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']
    recipes_cursor = recipes_db.find()

    #get the maximum and minimum sustainability scores

    max_overall = recipes_db.find_one(sort=[("overall_sustainability", -1)])['overall_sustainability']
    min_overall = recipes_db.find_one(sort=[("overall_sustainability", 1)])['overall_sustainability']

    for recipe in recipes_cursor:
        overall_sustainability = recipe['overall_sustainability']
        print("Recipe: ", recipe['title'])
        normalized_overall = (overall_sustainability - min_overall) / (max_overall - min_overall)
        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"sustainability_score": normalized_overall}})

    print("Done")

def produce_new_db_report():
    #Take the top 10 recipes from the cfp_sustainability perspective where the cfp_coverage is greater than 70%
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']    

    recipes_cursor = recipes_db.find({"percentage_covered_cfp": {"$gte": 70}}, sort=[("cfp_sustainability")], limit=10)

    #redirect the print output to a file
    sys.stdout = open("new_db_best_cfp.csv", "w")

    print("Top 10 recipes from the cfp_sustainability perspective")
    print("Recipe; CFP; URL")
    for recipe in recipes_cursor:
        print(recipe['title'], ';', recipe['cfp_sustainability'], ';', recipe['recipe_url'])

    sys.stdout.close()

    #Take the top 10 recipes from the wfp_sustainability perspective where the wfp_coverage is greater than 70%
    recipes_cursor = recipes_db.find({"percentage_covered_wfp": {"$gte": 70}}, sort=[("wfp_sustainability")], limit=10)

    #redirect the print output to a file
    sys.stdout = open("new_db_best_wfp.csv", "w")

    print("Top 10 recipes from the wfp_sustainability perspective")
    print("Recipe; WFP; URL")
    for recipe in recipes_cursor:
        print(recipe['title'],';', recipe['wfp_sustainability'],';', recipe['recipe_url'])
    
    sys.stdout.close()

    #Take the top 10 recipes from the sustainability_score perspective where both cfp_coverage and wfp_coverage are greater than 70%
    recipes_cursor = recipes_db.find({"percentage_covered_cfp": {"$gte": 70}, "percentage_covered_wfp": {"$gte": 70}}, sort=[("sustainability_score")], limit=10)

    #redirect the print output to a file
    sys.stdout = open("new_db_best_sustainability_score.csv", "w")

    print("Top 10 recipes from the sustainability_score perspective")
    print("Recipe; Sustainability Score; URL")
    for recipe in recipes_cursor:
        print(recipe['title'],';', recipe['sustainability_score'],';', recipe['recipe_url'])

    sys.stdout.close()

    #Teke the worst 10 recipes from the cfp_sustainability perspective where the cfp_coverage is greater than 70%
    recipes_cursor = recipes_db.find({"percentage_covered_cfp": {"$gte": 70}}, sort=[("cfp_sustainability", -1)], limit=10)
    #redirect the print output to a file
    sys.stdout = open("new_db_worst_cfp.csv", "w")

    print("Worst 10 recipes from the cfp_sustainability perspective")
    print("Recipe; CFP; URL")
    for recipe in recipes_cursor:
        print(recipe['title'],';', recipe['cfp_sustainability'],';', recipe['recipe_url'])
    
    sys.stdout.close()

    #Take the worst 10 recipes from the wfp_sustainability perspective where the wfp_coverage is greater than 70%
    recipes_cursor = recipes_db.find({"percentage_covered_wfp": {"$gte": 70}}, sort=[("wfp_sustainability", -1)], limit=10)

    #redirect the print output to a file
    sys.stdout = open("new_db_worst_wfp.csv", "w")

    print("Worst 10 recipes from the wfp_sustainability perspective")
    print("Recipe; WFP; URL")
    for recipe in recipes_cursor:
        print(recipe['title'],';', recipe['wfp_sustainability'],';', recipe['recipe_url'])
    
    sys.stdout.close()

    #Take the worst 10 recipes from the sustainability_score perspective where both cfp_coverage and wfp_coverage are greater than 70%
    recipes_cursor = recipes_db.find({"percentage_covered_cfp": {"$gte": 70}, "percentage_covered_wfp": {"$gte": 70}}, sort=[("sustainability_score", -1)], limit=10)

    #redirect the print output to a file
    sys.stdout = open("new_db_worst_sustainability_score.csv", "w")

    print("Worst 10 recipes from the sustainability_score perspective")
    print("Recipe; Sustainability Score; URL")
    for recipe in recipes_cursor:
        print(recipe['title'],';', recipe['sustainability_score'],';', recipe['recipe_url'])

    sys.stdout.close()

def produce_old_db_report():
    client = MongoClient('localhost', 27017)
    db = client['HeaSE']
    recipes_db = db['recipes']

    #Take the top 10 recipes from the sustainability_score perspective
    recipes_cursor = recipes_db.find(sort=[("sustainability_score")], limit=10)

    #redirect the print output to a file
    sys.stdout = open("old_db_best_sustainability_score.csv", "w")

    print("Top 10 recipes from the sustainability_score perspective in the old database")
    print("Recipe; Sustainability Score; URL")
    for recipe in recipes_cursor:
        print(recipe['title'],';', recipe['sustainability_score'],';', recipe['recipe_url'])

    sys.stdout.close()

    #Take the worst 10 recipes from the sustainability_score perspective
    recipes_cursor = recipes_db.find(sort=[("sustainability_score", -1)], limit=10)

    #redirect the print output to a file
    sys.stdout = open("old_db_worst_sustainability_score.csv", "w")


    print("Worst 10 recipes from the sustainability_score perspective in the old database")
    print("Recipe; Sustainability Score; URL")
    for recipe in recipes_cursor:
        print(recipe['title'],';', recipe['sustainability_score'],';', recipe['recipe_url'])

    sys.stdout.close()

def define_recipe_cluster():
    #connect to the database
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']

    #loop over the recipes
    recipes_cursor = recipes_db.find()

    for recipe in recipes_cursor:
        #if the sustainability score is in ]0, 0.04] then the recipe belongs to cluster 0
        if recipe['sustainability_score'] > 0 and recipe['sustainability_score'] <= 0.04:
            recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"sustainability_label": 0}})

        #if the sustainability score is in ]0.04, 0.15] then the recipe belongs to cluster 1
        if recipe['sustainability_score'] > 0.04 and recipe['sustainability_score'] <= 0.15:
            recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"sustainability_label": 1}})
        
        #if the sustainability score is in ]0.15, 1] then the recipe belongs to cluster 2
        if recipe['sustainability_score'] > 0.15 and recipe['sustainability_score'] <= 1:
            recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"sustainability_label": 2}})

    print("Done")

def add_original_ingredietn_list():
    #connect to the database
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']

    db_original = client['hummus_db']
    recipes_db_original = db_original['original_recipes']

    #loop over the recipes
    recipes_cursor = recipes_db.find()

    for recipe in recipes_cursor:
        #get the original recipe by recipe id
        original_recipe = recipes_db_original.find_one({"recipe_id": recipe['recipe_id']})
        if original_recipe is not None:
            original_ingredients = original_recipe['ingredients']
            print("Recipe: ", recipe['title'])
            recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"original_hummus_db_ingredients": original_ingredients}})

    print("Done")       

###### MAIN ######### 
'''  
compute_coverage()
compute_sustainability_scores()
compute_overall_sustainability_scores()
compute_normalized_sustainability_scores()
'''
#produce_new_db_report()
#produce_old_db_report()

define_recipe_cluster()

#add_original_ingredietn_list()