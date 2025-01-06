import jsonpickle
import service.domain.IngredientService as ingService
import service.domain.RecipeService as recipeService
import persistence.RecipePersistence as recipePersistence
import dto.Recipe as recipe
import pandas as pd
import numpy as np
import service.bot.EmbedderService as embedder
import service.domain.FoodHistoryService as foodHistory
import Utils

def get_base_recipe(mealDataJson):
    mealData = jsonpickle.decode(mealDataJson)
    ingredients = ingService.get_ingredient_list_from_generic_string(mealData['ingredients'])
    baseRecipe = recipe.Recipe(mealData["name"],None,ingredients,None,None,None,None)
    recipeService.compute_recipe_sustainability_score(baseRecipe)
    return  Utils.escape_curly_braces(jsonpickle.encode(baseRecipe))

def get_recipe_improved(mealDataJson, userData):
    mealData = jsonpickle.decode(mealDataJson)
    baseRecipe = jsonpickle.decode( Utils.de_escape_curly_braces(get_base_recipe(mealDataJson)))
    cluster = recipeService.get_recipe_cluster(baseRecipe)
    temporaryDeclinedSuggestions = foodHistory.get_temporary_declined_suggestions(userData.id)
    if temporaryDeclinedSuggestions != None and temporaryDeclinedSuggestions != '[]':
        #filter for not being in the user history
        temporaryDeclinedSuggestions = jsonpickle.decode(temporaryDeclinedSuggestions)
        temporaryDeclinedSuggestions = list(temporaryDeclinedSuggestions)
    else:
        temporaryDeclinedSuggestions = None
    if(cluster == 2):
        #will find a similar recipe in a lower cluster
        sustainableRecipes = recipePersistence.get_sustainable_recipe(None,temporaryDeclinedSuggestions)
    else:
        #will find a similar with an actuallly better sustainability score
        sustainableRecipes = recipePersistence.get_sustainable_recipe(baseRecipe.sustainability_score,temporaryDeclinedSuggestions)
    
    relatableRecipe = get_most_relatable_recipe(sustainableRecipes, mealData)
        #convert the recipe to a Recipe object
    suggestedRecipeEmealio = recipeService.convert_in_emealio_recipe(relatableRecipe,None)

    #convert the recipe to a string json
    suggestedRecipeStr = jsonpickle.encode(suggestedRecipeEmealio)

    #return the recipe in a json format
    return Utils.escape_curly_braces(suggestedRecipeStr)

def get_most_relatable_recipe(recipesList, mealData):
    baseRecipeIngredientsEmbedding = np.array([])
    baseRecipeIngredientsEmbeddingString = ', '.join(mealData['ingredients'])
    baseRecipeIngredientsEmbedding = embedder.embed_list(baseRecipeIngredientsEmbeddingString, False)
    #take only the columns ingredients_embedding and recipe_id
    list = [{"ingredients_embedding": np.array(obj["ingredients_embedding"]), "recipe_id": obj["recipe_id"]} for obj in recipesList]
    # convert the list to a pandas DataFrame
    list = pd.DataFrame(list)
    #calculate the cosine similarity between the desired ingredients and the ingredients of the recipe
    list['cosine_similarity'] = list.apply(lambda row: np.dot(row['ingredients_embedding'], baseRecipeIngredientsEmbedding)/(np.linalg.norm(row['ingredients_embedding'])*np.linalg.norm(baseRecipeIngredientsEmbedding)), axis=1)
    #sort the list by the taste score
    list = list.sort_values(by='cosine_similarity',ascending=False)
    #select the recipe with the highest taste score
    highesyScore = list.iloc[0]['recipe_id']
    #take from recipeList the recipe with the highest taste score
    recipe = next(item for item in recipesList if item["recipe_id"] == highesyScore)
    return recipe