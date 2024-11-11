import utils
start_recipe = """{
    "name":"Lasagna",
    "ingredients":"Lasagna, Hashed Meat, Tomato Sauce, Mozzarella",
    "carbonFootprint" : "0.5",
    "instruction" : "www.recipes.com/lasagna"
}"""

improved_recipe = """{
    "name":"Vegetarian Lasagna",
    "ingredients":"Lasagna, Spinach, Tomato Sauce, Ricotta",
    "carbonFootprint" : "0.4",
    "instruction" : "www.recipes.com/veglasagna"
}"""

def getRecipeSuggestion(recipe):
    recipe = recipe.strip().lower()
    if(recipe == "<lasagna>"):
        return [utils.escape_curly_braces(start_recipe), utils.escape_curly_braces(improved_recipe)]