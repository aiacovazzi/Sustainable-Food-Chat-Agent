import persistence.IngredientPersistence as ingredient_persistence
import persistence.RecipePersistence as recipe_persistence

#print(ingredient_persistence.get_most_similar_ingredient('special tomato'))

#print(ingredient_persistence.get_most_similar_ingredient('ultra pepper'))

print(recipe_persistence.get_most_similar_recipe("carobonara pasta"))

print(recipe_persistence.get_most_similar_recipe("spaghetti puttanesca"))

print("done")