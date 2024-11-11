import pandas as pd
from pymongo import MongoClient
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv, find_dotenv
import csv
MODEL = 'openai'
# Load environment variables from .env file
# Other available models:
# https://openai.com/api/pricing/
# gpt-3.5-turbo-0125
# gpt-4o-mini
# gpt-4o-2024-08-06
# gpt-4

SYSTEM_PROMPT = """Given a noisy text provided by the user:
Extract the ingredients' name using the simplest noun possible in singular form, like a vocabulary entry; then derive the related quantity using the availble information.
Quantities can be expressed in different ways, like in ounces, grams, cups, tablespoons, or units of the ingredient.
If you can't derive a quantity, just provide the ingredient's name. 
Do not made up quantities.
Use the following output structure:
['ingredient_name1 _ quantity1 __ unit of measure1', 'ingredient_name2 _ quantity2 __ unit of measure2', ... 'ingredient_nameN _ quantityN __ unit of measureN']
Do not output anything else outside what requested."""

load_dotenv(find_dotenv())

if(MODEL == 'openai'):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini")

def execute_chain(input_prompt, input_query, temperature):
    llm.temperature = temperature
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", input_prompt),
            ("human", "{query}"),
        ]
    )
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    answer = chain.invoke({ "query": input_query })
    return answer

#connect to mongodb
client = MongoClient('localhost', 27017)
db = client['hummus_db']
collection = db['original_recipes']

df = pd.read_csv('datasetUtilities\\data\\final_recipes_set.csv', quotechar='"')
total_cost = 0
index = 0
for index, row in df.iterrows():
    #check if the recipe is already cleaned
    if '__' in df.at[index, 'ingredients']:
        index += 1
        continue
    print('index: ' + str(index))
    #print('recipe_id:' + ' '+ str(row['recipe_id']))

    original_recipe = collection.find({ "recipe_id": row['recipe_id'] })
    original_recipe = list(original_recipe)

    #print('hease ingredients:' + ' '+ row['ingredients'])
    #print('hummus ingredients:' + ' '+ original_recipe[0]['ingredients'])

    ai_called = False

    while not ai_called:
        try:
            with get_openai_callback() as cb:
                cleaned_recipe = execute_chain(SYSTEM_PROMPT, original_recipe[0]['ingredients'], 0.1)
            ai_called = True
        except:
            print("AI call failed, retrying...")
    
    #print('cost: ' + str(cb.total_cost))
    total_cost += cb.total_cost
    #print('-------------------------------------')
    df.at[index, 'ingredients'] = cleaned_recipe
    #print('gpt_cleaned ingredients:' + ' '+ df.at[index, 'ingredients'] )

    #print the progress of the cleaning
    if (index % 100 == 0):
        print('index checkpoint: ' + str(index))
        print('total cost: ' + str(total_cost))
        print('percentage: ' + str((index/len(df))*100))
        #save the progress
        df.to_csv('datasetUtilities\data\cleaned_final_recipes_set.csv', index=False)

    index += 1

print('total cost: ' + str(total_cost))

#last saving
df.to_csv('datasetUtilities\data\cleaned_final_recipes_set.csv', index=False)

print("end")