import Utils
import jsonpickle
from pymongo import MongoClient
import numpy as np
import dto.Recipe as recipe
import service.domain.FoodHistoryService as foodHistory
import service.domain.RecipeService as recipeService
import service.bot.EmbedderService as embedder
import persistence.RecipePersistence as recipePersistence
import pandas as pd


    
def get_recipe_suggestion(mealDataJson, userData):

    #restriction and allergy and meal type must always be respected
    #the search will try to respect healthiness and meal duration if possible, but if no recipe is found that respects them, it will return a recipe that does not respect them
    #the system keeps track of the kind of constraints that are not respected in order to give the user a feedback about them
    
    queryTemplate =  """{ "$and": [ 
        { "sustainability_label": { "$in": [0, 1] } }, 
        { "percentage_covered_cfp": { "$gte": 70 } }, 
        { "percentage_covered_wfp": { "$gte": 70 } },
        {TAGS_SUSTAINABILITY},
        {TAGS_RESTRICTIONS},
        {ALLERGENES},
        {TAGS_MEAL_TYPE},
        {TAGS_USER_HISTORY},
        {TAGS_HEALTHINESS},
        {TAGS_MEAL_DURATION}
        ] }"""

    tagsSustainability = ""
    tagsRestrictions = ""   
    allergenes = ""
    tagsMealType = ""
    tagsUserHistory = ""
    tagsHealthiness = ""
    tagsMealDuration = ""
    projection = {"_id": 1, "recipe_id": 1, "title_embedding": 1, "ingredients_embedding": 1, "sustainability_score": 1} 

    #initializa as empty numpy array
    desiredIngredientsEmbedding = np.array([])
    notDesiredIngredientsEmbedding = np.array([])
    recipeNameEmbedding = np.array([])

    mealData = jsonpickle.decode(mealDataJson)

    if(mealData['recipeName'] != None and mealData['recipeName']  != ''):
        recipeNameEmbedding = embedder.embed_sentence(mealData['recipeName'])

    if(mealData['ingredients_desired'] != None and mealData['ingredients_desired']  != ''):
        desiredIngredientsEmbeddingString = ', '.join(mealData['ingredients_desired'])
        desiredIngredientsEmbedding = embedder.embed_list(desiredIngredientsEmbeddingString, False)
    
    if(mealData['ingredients_not_desired'] != None and mealData['ingredients_not_desired']  != ''):
        notDesiredIngredientsEmbeddingString = ', '.join(mealData['ingredients_not_desired'])
        notDesiredIngredientsEmbedding = embedder.embed_list(notDesiredIngredientsEmbeddingString, False)
    
    #connect to mongodb
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes = db['recipes']

    #filter for the sustainability score
    if(mealData['sustainabilityScore'] != ""):
        tagsSustainability = """ "sustainability_score": { "$lt": SUSTAINABILITY_VALUE } """
        tagsSustainability = tagsSustainability.replace("SUSTAINABILITY_VALUE",str(mealData['sustainabilityScore']))

    #filter for the restrictions
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
    #no meal type specified, take all the meal types as filter
    #else:
    #    tagsMealType = """ "$or": [
    #    "$and": [{ "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "dinner" } }],
    #    "$and": [{ "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "lunch" } }],
    #    "tags": { "$regex": "breakfast" },
    #    "tags": { "$regex": "snack" }
    #    ] """

    #obtain the user history
    userHistory = foodHistory.get_user_history_of_week(userData.id, False)
    if userHistory != None and userHistory != '[]':
        #filter for not being in the user history
        userHistory = jsonpickle.decode(userHistory)
        tagsUserHistory = """"recipe_id": {"$nin": ["""
        for history in userHistory:
            tagsUserHistory +=  str(history['recipeId']) + ","
        tagsUserHistory = tagsUserHistory[:-1]
        tagsUserHistory += "] }"

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
    mandatoryReplacement = [["TAGS_SUSTAINABILITY",tagsSustainability],["TAGS_RESTRICTIONS",tagsRestrictions],["ALLERGENES",allergenes],["TAGS_MEAL_TYPE",tagsMealType]]
    notMadatoryReplacement = [["TAGS_USER_HISTORY",tagsUserHistory],["TAGS_HEALTHINESS",tagsHealthiness],["TAGS_MEAL_DURATION",tagsMealDuration]]

    numberOfFoundRecipes = 0
    numReplacement = len(notMadatoryReplacement)

    removedConstraints = []

    while(numberOfFoundRecipes == 0 and numReplacement > 0):
        query = query_template_replacement(mandatoryReplacement, notMadatoryReplacement,numReplacement,queryTemplate)
        #convert query in a dict
        query = jsonpickle.decode(query)
        suggestedRecipes = recipes.find(query,projection)
        numberOfFoundRecipes = recipes.count_documents(query)
        numReplacement -= 1

        #remove a constraint if actually was valored
        if(numberOfFoundRecipes == 0 and notMadatoryReplacement[numReplacement][1]!=""):
            removedConstraints.append(notMadatoryReplacement[numReplacement][0])
    
    if(numberOfFoundRecipes == 0):
        #no recipe found
        return None
    
    #order the suggested recipes by the sustainability score (the lower the better) // this is useful for the case in which the user does not have any preference so the system will suggest the most sustainable recipe
    suggestedRecipes = suggestedRecipes.sort("sustainability_score")

    suggestedRecipes = list(suggestedRecipes)

    suggestedRecipe = get_preferable_recipe_by_taste(suggestedRecipes,desiredIngredientsEmbedding,notDesiredIngredientsEmbedding,recipeNameEmbedding)

    #get the full recipe from the database
    suggestedRecipe = jsonpickle.decode(recipePersistence.get_recipe_by_id(int(suggestedRecipe["recipe_id"])))

    #convert the recipe to a Recipe object
    suggestedRecipe = recipeService.convert_in_emealio_recipe(suggestedRecipe,removedConstraints)

    #convert the recipe to a string json
    suggestedRecipeStr = suggestedRecipe.to_json()

    #return the recipe in a json format
    return Utils.escape_curly_braces(suggestedRecipeStr)

def query_template_replacement (mandatoryRepalcement, notMandatoryReplacement, numberReplacement, queryTemplate):
    for replacement in mandatoryRepalcement:
        queryTemplate = queryTemplate.replace(replacement[0],replacement[1])

    for replacement in range(0,numberReplacement):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],str(notMandatoryReplacement[replacement][1]))

    remainingReplacement = len(notMandatoryReplacement) - numberReplacement

    #clean the query from the not mandatory replacement that are not used
    for replacement in range(len(notMandatoryReplacement)-remainingReplacement,len(notMandatoryReplacement)):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],"")

    return queryTemplate

def get_preferable_recipe_by_taste(recipeList, desiredIgredientsEmbeddings, notDesiredIgredientsEmbeddings,recipeNameEmbedding):
    #if both desiredIgredientsEmbeddings and notDesiredIgredientsEmbeddings are None then return the first recipe
    if(len(desiredIgredientsEmbeddings) == 0 and len(notDesiredIgredientsEmbeddings) == 0):
        return recipeList[0]

    #take only the columns ingredients_embedding and recipe_id
    #list = [{"ingredients_embedding": np.array(obj["ingredients_embedding"]), "title_embedding": np.array(obj["title_embedding"]), "recipe_id": obj["recipe_id"]} for obj in recipeList]

    # convert the list to a pandas DataFrame
    list = pd.DataFrame(recipeList)

    if(len(desiredIgredientsEmbeddings) != 0):
        #calculate the cosine similarity between the desired ingredients and the ingredients of the recipe
        list['cosine_similarity_desired'] = list.apply(lambda row: np.dot(row['ingredients_embedding'], desiredIgredientsEmbeddings)/(np.linalg.norm(row['ingredients_embedding'])*np.linalg.norm(desiredIgredientsEmbeddings)), axis=1)

    if(len(notDesiredIgredientsEmbeddings) != 0):
        #calculate the cosine similarity between the not desired ingredients and the ingredients of the recipe
        list['cosine_similarity_not_desired'] = list.apply(lambda row: np.dot(row['ingredients_embedding'], notDesiredIgredientsEmbeddings)/(np.linalg.norm(row['ingredients_embedding'])*np.linalg.norm(notDesiredIgredientsEmbeddings)), axis=1)

    if(len(recipeNameEmbedding) != 0):
        #calculate the cosine similarity between the recipe name of the base recipe and the recipe name of the target recipe
        list['cosine_similarity_recipe_name'] = list.apply(lambda row: np.dot(row['title_embedding'], recipeNameEmbedding)/(np.linalg.norm(row['title_embedding'])*np.linalg.norm(recipeNameEmbedding)), axis=1)

    #take the recipe who maximizes the cosine similarity with the desired ingredients and minimizes the cosine similarity with the not desired ingredients
    if(len(desiredIgredientsEmbeddings) != 0 and len(notDesiredIgredientsEmbeddings) != 0):
        list['taste_score'] = list['cosine_similarity_desired'] - list['cosine_similarity_not_desired']
    #take the recipe who maximizes the cosine similarity with the desired ingredients and the recipe name // this in order to guide the recipe improver to suggest a recipe that is similar to the base recipe
    elif(len(desiredIgredientsEmbeddings) != 0 and len(recipeNameEmbedding) != 0):
        list['taste_score'] = list['cosine_similarity_desired'] + list['cosine_similarity_recipe_name']
    elif(len(desiredIgredientsEmbeddings) != 0 ):
        list['taste_score'] = list['cosine_similarity_desired']
    elif(len(notDesiredIgredientsEmbeddings) != 0):
        list['taste_score'] = -list['cosine_similarity_not_desired']
    
    #sort the list by the taste score
    list = list.sort_values(by='taste_score',ascending=False)

    #select the recipe with the highest taste score
    highestTasteScoreRecipe = list.iloc[0]

    return highestTasteScoreRecipe