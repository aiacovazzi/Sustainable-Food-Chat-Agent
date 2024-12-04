import pandas as pd
df = pd.read_csv('datasetUtilities\data\cleaned_final_recipes_set.csv', quotechar='"')

#2024/12/02:
#the extraction is flawed since some ingredientns contain commas, and others contant underscores
#this is a small problem that can be overcome a-posteriori by insert manually the missing ingredients

#define an hasmap to store the ingredients along with the id of the recipe they belong to
ingredients = {}

#loop over the df and extract the ingredients
for index, row in df.iterrows():
    #get the ingredients of the recipe
    for ingredient in row['ingredients'].split(','):
        #remove the characters '[', ']' and ''' from the ingredient
        ingredient = ingredient.replace('[','').replace(']','').replace('\'','').replace('\"','')
        #remove the characters '_' and everithing after it
        ingredient = ingredient.split('_')[0] 
        #remove trailing and leading whitespaces
        ingredient = ingredient.strip()
        #add the ingredient to the hashmap
        if ingredient in ingredients:
            ingredients[ingredient].append(row['recipe_id'])
        else:
            ingredients[ingredient] = [row['recipe_id']]

#order the ingredients by the number of recipes they appear in
ingredients = dict(sorted(ingredients.items(), key=lambda item: len(item[1]), reverse=True))

df = pd.DataFrame(list(ingredients.items()), columns=['ingredient', 'recipe_id'])
df.to_csv('datasetUtilities\data\ingredients.csv', index=False)




#transform the array into an hash table that counts the number of times each ingredient appears
'''from collections import Counter
ingredientCounter = Counter(ingredients)
#order the hash table by the number of appearances
ingredientCounter = dict(sorted(ingredientCounter.items(), key=lambda item: item[1], reverse=True))
print(ingredientCounter)

#save the hash table into a csv file
df = pd.DataFrame(list(ingredientCounter.items()), columns=['ingredient', 'count'])
df.to_csv('datasetUtilities\\data\\ingredients.csv', index=False)'''