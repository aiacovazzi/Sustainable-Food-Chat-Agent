import os
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks import get_openai_callback
K = 3
MODEL = 'openai'
SYSTEM_PROMPT_ING = """Given an ingredient name, choose the most relatable ingredient from the list analyzing it element by element. A list could have no relatable ingredients. Write ONLY the name of the matched ingredient as reported in quotes. If there are no relatable ingredients, return "NO_MATCH."""

SYSTEM_PROMPT_TYP = """Given an ingredient name, choose the most relatable typology from the list analyzing it element by element. A list could have no relatable typologies. Write ONLY the name of the matched typology as reported in quotes. If there are no relatable typologies, return "NO_MATCH."""

if(MODEL == 'openai'):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o")

def execute_chain(input_prompt, input_query, temperature):
    llm.temperature = temperature
    llm.max_tokens = 50
    llm.top_p = 1.0
    llm.frequency_penalty = 0.0
    llm.presence_penalty = 0.0
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

def errorRow(ingredient):
    return pd.DataFrame([{
                'ingredient': i,
                'cfp': np.nan,
                'wfp': np.nan,
                'mapping_type': 'ERROR',
                'mapped_item': 'ERROR'
            }])

ingredient_list = pd.read_csv('datasetUtilities\\data\\ingredients.csv', quotechar='"')

csel_ingredients = pd.read_csv('datasetUtilities\\data\\CSEL data\\cfp_wfp_ingredients.csv', quotechar='"', sep=';')
csel_typologies = pd.read_csv('datasetUtilities\\data\\CSEL data\\cfp_wfp_typologies.csv', quotechar='"' , sep=';')
f = open('datasetUtilities\\data\\CSEL data\\mapper_log.txt','w')


model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
csel_ingredients_embeddings = model.encode(csel_ingredients['Food commodity ITEM'])
csel_typologies_embeddings = model.encode(csel_typologies['Food commodity TYPOLOGY'])

#create an empty dataframe to store the results
results = pd.DataFrame(columns=['ingredient', 'cfp', 'wfp', 'mapping_type', 'mapped_item'])

number = 0
for i in ingredient_list['ingredient']:
    #if number >= 50:
    #    break
    print(i, file=f)
    #find the K most similar ingredients in the CSEL dataset

    #get the embeddings of the ingredient
    ingredient_embedding = model.encode(i)
    #calculate the cosine similarity between the ingredient and the CSEL dataset
    similarity = cosine_similarity([ingredient_embedding], csel_ingredients_embeddings)
    #get the K most similar ingredients
    similar_ingredients = np.argsort(similarity[0])[-K:]
    #order the ingredients by similarity
    similar_ingredients = similar_ingredients[::-1]
    #print the ingredient and the K most similar ingredients
    str = 'Ingredient: ' + i + '\n'
    str += 'Similar ingredients: ['
    for j in similar_ingredients:
        str += '"'+csel_ingredients['Food commodity ITEM'][j] + '"; '
    str += ']'
    print(str, file=f)

    #call the model to get the most similar ingredient
    answer = execute_chain(SYSTEM_PROMPT_ING, str, 0)

    answer = answer.replace('"', '')

    if(answer != 'NO_MATCH'):
        #print('Most similar ingredient: ' + answer)
        #print('______________________________________________________')
        #given the answer, get the index of the array similar_ingredients that corresponds to the answer
        print(answer, file=f)
        try:
            index = np.where(csel_ingredients['Food commodity ITEM'] == answer)
            index = index[0][0]
            new_row = pd.DataFrame([{
                'ingredient': i,
                'cfp': csel_ingredients['final_co2'][index],
                'wfp': csel_ingredients['final_wfp'][index],
                'mapping_type': 'ingredient',
                'mapped_item': answer
            }])
        except:
            new_row = errorRow(i)
        print(new_row, file=f)
        results = pd.concat([results, new_row], ignore_index=True)
    else:
        #calculate the cosine similarity between the ingredient and the typology CSEL dataset
        similarity = cosine_similarity([ingredient_embedding], csel_typologies_embeddings)
        #get the K most similar typologies
        similar_typologies = np.argsort(similarity[0])[-K:]
        #order the typologies by similarity
        similar_typologies = similar_typologies[::-1]
        #print the ingredient and the K most similar typologies
        str = 'Ingredient: ' + i + '\n'
        str += 'Similar typologies: ['
        for j in similar_typologies:
            str += '"'+csel_typologies['Food commodity TYPOLOGY'][j] + '"; '
        str += ']'
        print(str, file=f)

        #call
        answer = execute_chain(SYSTEM_PROMPT_TYP, str, 0)
        answer = answer.replace('"', '')
        #print('Most similar typology: ' + answer)
        
        if(answer != 'NO_MATCH'):
            #given the answer, get the index of the array similar_typologies that corresponds to the answer
            try:
                index = np.where(csel_typologies['Food commodity TYPOLOGY'] == answer)
                index = index[0][0]
                new_row = pd.DataFrame([{
                    'ingredient': i,
                    'cfp': csel_typologies['final_co2'][index],
                    'wfp': csel_typologies['final_wfp'][index],
                    'mapping_type': 'typology',
                    'mapped_item': answer
                }])
            except:
                new_row = errorRow(i)
        else:
            new_row = pd.DataFrame([{
                'ingredient': i,
                'cfp': np.nan,
                'wfp': np.nan,
                'mapping_type': 'no_match',
                'mapped_item': 'NO_MATCH'
            }])
        print(new_row, file=f)
        results = pd.concat([results, new_row], ignore_index=True)
    number = number + 1
    print('______________________________________________________', file=f)

results.to_csv('datasetUtilities\\data\\ingredients_mapping.csv', index=False)
print('Mapping done!', file=f)