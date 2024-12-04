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

no_match = pd.read_csv('datasetUtilities\\data\\ingredients_work_in_progress\\no_match.csv', quotechar='"', sep=';')

matched = pd.read_csv('datasetUtilities\\data\\ingredients_work_in_progress\\matched.csv', quotechar='"', sep=';')

f = open('datasetUtilities\\data\\ingredients_work_in_progress\\self_mapper_log.txt','w', encoding="utf-8")


model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
matched_embedding = model.encode(matched['ingredient'])


#create an empty dataframe to store the results
results = pd.DataFrame(columns=['ingredient', 'cfp', 'wfp', 'mapping_type', 'mapped_item','data_origin','notes'])

number = 0
for i in no_match['ingredient']:
    #if number >= 50:
    #    break
    print(i, file=f)
    #find the K most similar ingredients in the CSEL dataset

    #get the embeddings of the ingredient
    ingredient_embedding = model.encode(i)
    #calculate the cosine similarity between the ingredient and the CSEL dataset
    similarity = cosine_similarity([ingredient_embedding], matched_embedding)
    #get the K most similar ingredients
    similar_ingredients = np.argsort(similarity[0])[-K:]
    #order the ingredients by similarity
    similar_ingredients = similar_ingredients[::-1]
    #print the ingredient and the K most similar ingredients
    str = 'Ingredient: ' + i + '\n'
    str += 'Similar ingredients: ['
    for j in similar_ingredients:
        str += '"'+matched['ingredient'][j] + '"; '
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
            index = np.where(matched['ingredient'] == answer)
            index = index[0][0]
            new_row = pd.DataFrame([{
                'ingredient': i,
                'cfp': matched['cfp'][index],
                'wfp': matched['wfp'][index],
                'mapping_type': matched['mapping_type'][index],
                'mapped_item': matched['mapped_item'][index],
                'data_origin': matched['data_origin'][index],
                'notes': 'Self-mapped',
            }])
        except:
            new_row = errorRow(i)
        print(new_row, file=f)
        results = pd.concat([results, new_row], ignore_index=True)
    else:
        new_row = pd.DataFrame([{
            'ingredient': i,
            'cfp': np.nan,
            'wfp': np.nan,
            'mapping_type': 'NO_MATCH',
            'mapped_item': 'NO_MATCH',
            'data_origin': None,
            'notes': None,
        }])
        print(new_row, file=f)
        results = pd.concat([results, new_row], ignore_index=True)
    number = number + 1
    print('______________________________________________________', file=f)

results.to_csv('datasetUtilities\\data\\no_match_mapping.csv', index=False)
print('Mapping done!', file=f)