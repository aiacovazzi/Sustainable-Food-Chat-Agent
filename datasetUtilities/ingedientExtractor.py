import pandas as pd
df = pd.read_csv('data\\sample\\cleanedSampleOf100RecipesHeaSE.csv', quotechar='"')

#define an array to store the ingredients
ingredients = []

for i in df['ingredients']:
    for ingredient in i.split(','):
        #remove the characters '[', ']' and ''' from the ingredient
        ingredient = ingredient.replace('[','').replace(']','').replace('\'','')
        #remove the characters '_' and everithing after it
        ingredient = ingredient.split('_')[0] 
        #remove trailing and leading whitespaces
        ingredient = ingredient.strip()
        #add the ingredient to the array
        ingredients.append(ingredient)

print(len(ingredients))

#transform the array into an hash table that counts the number of times each ingredient appears
from collections import Counter
ingredientCounter = Counter(ingredients)
print(ingredientCounter)