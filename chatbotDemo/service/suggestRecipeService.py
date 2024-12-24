import utils
import jsonpickle
from pymongo import MongoClient
import numpy as np
import dto.recipe as recipe

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

def queryTemplateReplacement (mandatoryRepalcement, notMandatoryReplacement, numberReplacement, queryTemplate):
    for replacement in mandatoryRepalcement:
        queryTemplate = queryTemplate.replace(replacement[0],replacement[1])

    for replacement in range(0,numberReplacement):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],str(notMandatoryReplacement[replacement][1]))

    remainingReplacement = len(notMandatoryReplacement) - numberReplacement

    #clean the query from the not mandatory replacement that are not used
    for replacement in range(len(notMandatoryReplacement)-remainingReplacement,len(notMandatoryReplacement)):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],"")

    return queryTemplate
    
def getRecipeSuggestion(mealDataJson, userData):

    #restriction and allergy and meal type must always be respected
    #the search will try to respect healthiness and meal duration if possible, but if no recipe is found that respects them, it will return a recipe that does not respect them
    #the system keeps track of the kind of constraints that are not respected in order to give the user a feedback about them
    
    queryTemplate =  """{ "$and": [ 
        { "sustainability_label": { "$in": [0, 1] } }, 
        { "percentage_covered_cfp": { "$gte": 70 } }, 
        { "percentage_covered_wfp": { "$gte": 70 } },
        {TAGS_RESTRICTIONS},
        {ALLERGENES},
        {TAGS_MEAL_TYPE},
        {TAGS_HEALTHINESS},
        {TAGS_MEAL_DURATION}
        ] }"""

    tagsRestrictions = ""   
    allergenes = ""
    tagsMealType = ""
    tagsMealDuration = ""
    tagsHealthiness = ""

    mealData = jsonpickle.decode(mealDataJson)
    
    #connect to mongodb
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes = db['recipes']


    #filrter for the restrictions
    restrictions = userData.restrictions
    if(restrictions != None and restrictions != ''):
        tagsRestrictions = """ "$and": [ """
        for restriction in restrictions:
            tagsRestrictions += """ {"tags": { "$regex": "%s" }}, """ % restriction
        tagsRestrictions = tagsRestrictions[:-2]
        tagsRestrictions += """ ] """


    #filter for the allergies 
    allergies = userData.allergies
    if(allergies != None and allergies != ''):
        allergenes = """ "$and": [ """
        for allergen in allergies:
            allergenes += """ {"allergies": { "$regex": "%s" }}, """ % allergen
        allergenes = allergenes[:-2]
        allergenes += """ ] """

    #temporary override for the allergenes because the database is not updated
    allergenes = ""


    #filter for the meal type    
    mealType = mealData['mealType']
    if(mealType == "Dinner"):
        tagsMealType = """ "$and": [{ "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "dinner" } }] """
    elif(mealType == "Lunch"):
        tagsMealType = """ "$and": [ { "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "lunch" } } ] """
    elif(mealType == "Breakfast"):
        tagsMealType = """ "tags": { "$regex": "breakfast" } """
    elif(mealType == "Snack"):
        tagsMealType = """ "tags": { "$regex": "snack" } """

    #filter for the healthiness
    healthiness = mealData['healthiness']
    if(healthiness == "yes"):
        tagsHealthiness = """ "healthiness_label": 0 """

    #filter for the meal duration
    cookingTime = mealData['cookingTime']
    if(cookingTime == "short"):
        tagsMealDuration = """ "tags": { "$regex": "15-minutes-or-less" } """
    elif(cookingTime == "medium"):
        tagsMealDuration = """ "tags": { "$regex": "30-minutes-or-less" } """

    #replace the tags in the query template
    mandatoryReplacement = [["TAGS_RESTRICTIONS",tagsRestrictions],["ALLERGENES",allergenes],["TAGS_MEAL_TYPE",tagsMealType]]
    notMadatoryReplacement = [["TAGS_MEAL_DURATION",tagsMealDuration],["TAGS_HEALTHINESS",tagsHealthiness]]

    numberOfFoundRecipes = 0
    numReplacement = 2

    removedConstraints = []

    while(numberOfFoundRecipes == 0 and numReplacement > 0):
        query = queryTemplateReplacement(mandatoryReplacement, notMadatoryReplacement,numReplacement,queryTemplate)
        #convert query in a dict
        query = jsonpickle.decode(query)
        #query the database
        suggestedRecipes = recipes.find(query)
        #count the number of suggested recipes
        numberOfFoundRecipes = recipes.count_documents(query)
        numReplacement -= 1

        #remove a constraint if actually was valored
        if(numberOfFoundRecipes == 0 and notMadatoryReplacement[numReplacement][1]!=""):
            removedConstraints.append(notMadatoryReplacement[numReplacement][0])
    
    if(numberOfFoundRecipes == 0):
        #no recipe found
        return None

    #loop through the suggested recipes
    suggestedRecipes = list(suggestedRecipes)

    #take one random recipe // for now take the first one // later we will implement a scoring system
    suggestedRecipe = suggestedRecipes[0]

    #convert the recipe to a Recipe object
    suggestedRecipe = convertInEmealioRecipe(suggestedRecipe,removedConstraints)

    #convert the recipe to a string json
    suggestedRecipeStr = suggestedRecipe.to_json()

    #return the recipe in a json format
    return utils.escape_curly_braces(suggestedRecipeStr)

def convertInEmealioRecipe(mongoRecipe,removedConstraints):
    title = mongoRecipe['title']
    id = mongoRecipe['recipe_id']
    instructions = mongoRecipe['recipe_url']
    sustainabilityScore = mongoRecipe['sustainability_score']
    #check if the description is present
    if 'description' in mongoRecipe:
        description = mongoRecipe['description']
    else:
        description = None
    ingredients = getIngredientInfo(mongoRecipe['ingredients'])
    return recipe.Recipe(title,id,ingredients,sustainabilityScore,instructions,description,removedConstraints)

def getIngredientInfo(ingredients):
    #connect to mongodb
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    ingredientsDB = db['ingredients']

    ingredients = get_ingredients(ingredients)
    ingredientObjList = []
    for ingredient in ingredients:
        #query the database
        ingredientInDB = ingredientsDB.find_one({"ingredient":ingredient})

        #if the ingredienntDB has the cfp data then use it else use None
        if 'cfp' in ingredientInDB:
            cfp = ingredientInDB['cfp']
        else:
            cfp = None

        #if the ingredienntDB has the wfp data then use it else use None
        if 'wfp' in ingredientInDB:
            wfp = ingredientInDB['wfp']
        else:
            wfp = None

        ingredientObjList.append(recipe.Food(ingredient,cfp,wfp))
    
    return ingredientObjList