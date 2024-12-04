import pandas as pd
import math
def remove_additional_info(ingredient):
    #given a string like "water _ 2 __ cups"
    #find the  index of the character "_" and remove everything after it
    index = ingredient.find(' _')
    #if the character is not found then return the string as it is
    if index != -1:
        #get the substring from 0 to the index minus 1
        ingredient = ingredient[:index]
    #remove [,],{,} and '
    ingredient = ingredient.replace('[','')
    ingredient = ingredient.replace(']','')
    ingredient = ingredient.replace('{','')
    ingredient = ingredient.replace('}','')
    ingredient = ingredient.replace('"','')
    ingredient = ingredient.replace('\'','')
    #remove trailing and leading spaces
    return ingredient

def get_ingredients(ingredients):
    ingredients = ingredients.split("',")
    ingredients = [ingredient.strip() for ingredient in ingredients]
    ingredients = [remove_additional_info(ingredient) for ingredient in ingredients]
    ingredients = set(ingredients)
    return ingredients

def count_covered(idx,dataframe, ingredient_list, missing_ingredients_set):
    covered = 0

    for i in ingredient_list:
        #check i in dataframe
        if i in dataframe['ingredient'].values:
            #if it has the cfp value then it is covered 
            cfp = dataframe[dataframe['ingredient'] == i]['wfp'].values[0]
            #convert to float and check if it is nan
            if(type(cfp) == str):
                cfp = float(cfp.replace(',','.'))

            if not math.isnan(cfp):
                covered += 1
            else:
                print('wfp not found for ingredient: ', i)
        else:
            print(idx)
            print('ingredient not found: ', i)
            print(ingredient_list)
            missing_ingredients_set.add(i)

    return covered

df = pd.read_csv('datasetUtilities\\data\\cleaned_final_recipes_set.csv', quotechar='"', sep=',',encoding='utf-8')
df_ingredients = pd.read_csv('datasetUtilities\\data\\ingredients_work_in_progress\\5_full_integrated_ingredient_dataset\\full_integrated_ingredient_dataset.csv', sep=';',encoding='utf-8')
f = open('datasetUtilities\\data\\ingredient_coverage.txt','w')

missing_ingredients = set()
i = 1
not_100_percent = 0
#for index, row in df.head(1000).iterrows():
for index, row in df.iterrows():
    #take the ingredients column
    ingredients = row['ingredients']
    #print(ingredients)
    ingredients_ = get_ingredients(ingredients)
    total_ingredients = len(ingredients_)
    count_covered_ = count_covered(i,df_ingredients, ingredients_, missing_ingredients)
    #percentage of ingredients covered
    percentage_covered = count_covered_/total_ingredients
    if percentage_covered != 1:
        #print(i,count_covered_/total_ingredients)
        f.write(str(i) + ',' + str(percentage_covered) + '\n')
        not_100_percent += 1
    i += 1
#print('total recipes: ', i)    
#print('not 100 percent: ', not_100_percent)
f.write('total recipes: ' + str(i) + '\n')
f.write('not 100 percent: ' + str(not_100_percent) + '\n')

f.write('missing ingredients: \n')
for i in missing_ingredients:
    f.write(i + '\n')
f.close()