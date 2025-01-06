import jsonpickle
import service.domain.IngredientService as ingService
import service.domain.RecipeService as recipeService
import persistence.RecipePersistence as recipePersistence
import dto.Recipe as recipe
import pandas as pd
import numpy as np
import service.bot.EmbedderService as embedder
import service.domain.FoodHistoryService as foodHistory
import service.SuggestRecipeService as food
import Utils

def get_base_recipe(mealDataJson):
    mealData = jsonpickle.decode(mealDataJson)
    ingredients = ingService.get_ingredient_list_from_generic_string(mealData['ingredients'])
    baseRecipe = recipe.Recipe(mealData["name"],None,ingredients,None,None,None,None)
    recipeService.compute_recipe_sustainability_score(baseRecipe)
    return  Utils.escape_curly_braces(jsonpickle.encode(baseRecipe))

def get_recipe_improved(baseRecipe, userData):
    baseRecipe = jsonpickle.decode(Utils.de_escape_curly_braces(baseRecipe))
    ingredients = baseRecipe.ingredients
    ingredientsString = ', '.join([ingredient.name for ingredient in ingredients])

    info = """{ mealType: "", 
                recipeName: RECIPE_NAME,
                ingredients_desired: INGREDIENTS_DESIRED,
                ingredients_not_desired: "",
                cookingTime: "",
                healthiness: ""} """
    
    info = info.replace("INGREDIENTS_DESIRED", "["+ingredientsString+"]")
    info = info.replace("RECIPE_NAME", baseRecipe.name)
    
    suggestedRecipe = food.get_recipe_suggestion(info,userData)
    return suggestedRecipe