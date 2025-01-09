import service.ImproveRecipeService as irs
import jsonpickle
import Utils

def extractRecipes(recipesData):
    recipesNames = recipesData['recipeNames']
    recipesIngredients = recipesData['recipeIngredients']    
    recipes = []

    for name in recipesNames:
        mealData = {'name': name, 'ingredients': []}
        baseRecipe = jsonpickle.decode(Utils.de_escape_curly_braces(irs.get_base_recipe(jsonpickle.encode(mealData))))
        recipes.append(baseRecipe)

    for ingredients in recipesIngredients:
        mealData = {'name': None,'ingredients': ingredients}
        baseRecipe = jsonpickle.decode(Utils.de_escape_curly_braces(irs.get_base_recipe(jsonpickle.encode(mealData))))
        recipes.append(baseRecipe)

    return Utils.escape_curly_braces(jsonpickle.encode(recipes))
    

        