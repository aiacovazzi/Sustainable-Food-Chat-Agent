import utils
recipe1 = """{
    "name":"Veg Burger",
    "ingredients":"Buns, Lattuce, Tomato, Lentils Burger, Veg Mayo",
    "carbonFootprint" : "0.3",
    "instruction" : "www.recipes.com/vegburger"
}"""

recipe2 = """{
    "name":"Pasta Crudaiola",
    "ingredients":"Pasta, Fresh Tomatoes, Basil, Mozzarella",
    "carbonFootprint" : "0.4",
    "instruction" : "www.recipes.com/crudaiola"
}"""

def getRecipeSuggestion(mealType):
    mealType = mealType.strip()
    if(mealType == "[Dinner]"):
        return utils.escape_curly_braces(recipe1)
    else:
        return utils.escape_curly_braces(recipe2)