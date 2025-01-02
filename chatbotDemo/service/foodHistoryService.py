import persistence.UserHistoryPersistence as userHistoryDB
from datetime import datetime, timedelta
import jsonpickle
import dto.userHistory as uh
import dto.recipe as recipe
import persistence.IngredientPersistence as ingredientDB
import service.recipeService as recipeService

def get_user_history_of_week(userId, onlyAccepted = True):
    #get the user history of the week
    fullUserHistory = userHistoryDB.get_user_history(userId)

    if fullUserHistory == None:
        return None

    fullUserHistory = jsonpickle.decode(fullUserHistory)
    #filter the user history of the week
    sysdate = datetime.today()
    previousWeek = sysdate - timedelta(days=7)
    userHistory = []
    for history in fullUserHistory:
        date = datetime.strptime(history['date'], '%Y-%m-%d %H:%M:%S')
        if date >= previousWeek and date <= sysdate and (not onlyAccepted or history['status'] == 'accepted'or history['status'] == 'asserted'):
            userHistory.append(history)
    return jsonpickle.encode(userHistory)

def clean_temporary_declined_suggestions(userId):
    userHistoryDB.clean_temporary_declined_suggestions(userId)

def save_user_history(userHistoryJson):
    userHistoryDB.save_user_history(userHistoryJson)

def build_and_save_user_history(userData, jsonRecipe, status):
    suggestedRecipe = recipe.Recipe(None,None,None,None,None,None,None)
    suggestedRecipe.from_json(jsonRecipe)
    sysdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    userHistory = uh.UserHistory(userData.id, suggestedRecipe.id, suggestedRecipe, sysdate, status)
    #save the suggestion in the user history
    save_user_history(userHistory.to_plain_json())

def build_and_save_user_history_from_user_assertion(userData, jsonRecipeAssertion):
    recipeAssertion = jsonpickle.decode(jsonRecipeAssertion)

    ingredients = []

    for ingredient in recipeAssertion['listOfFoods']:
        foodFromDB= ingredientDB.get_ingredient_by_name(ingredient)
        if foodFromDB == None or foodFromDB == 'null':
            foodFromDB = ingredientDB.get_most_similar_ingredient(ingredient)
        foodFromDB = jsonpickle.decode(foodFromDB)
        food = recipe.Food(ingredient, foodFromDB['cfp'], foodFromDB['wfp'])
        ingredients.append(food)

    sustanaibilityScore = None
    sysdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    assertedRecipe = recipe.Recipe(recipeAssertion["name"],None,ingredients,sustanaibilityScore,None,None,None)
    recipeService.compute_recipe_sustainability_score(assertedRecipe)
    userHistory = uh.UserHistory(userData.id, None, assertedRecipe, sysdate, 'asserted')
    save_user_history(userHistory.to_plain_json())