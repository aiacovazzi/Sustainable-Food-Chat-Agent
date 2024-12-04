import os
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np

no_match_checked = pd.read_csv('datasetUtilities\\data\\ingredients_work_in_progress\\4_splitted_dataset\\no_match_mapping_checked_csv.csv', quotechar='"', sep=';',encoding='cp1252')

full_dataset = pd.read_csv('datasetUtilities\\data\\ingredients_work_in_progress\\4_splitted_dataset\\full_ingredient_dataset_csv.csv', quotechar='"', sep=';',encoding='cp1252')

#create an empty dataframe to store the results
results = pd.DataFrame(columns=['ingredient', 'cfp', 'wfp', 'mapping_type', 'mapped_item','data_origin','notes'])

#loop over full dataset
for i in full_dataset['ingredient']:
    #if mapped_item id NO_MATCH, then we need to check if it is in the no_match_checked dataset
    if full_dataset.loc[full_dataset['ingredient'] == i]['mapped_item'].values[0] == 'NO_MATCH':
        #take the row from no_match_checked dataset
        row = no_match_checked.loc[no_match_checked['ingredient'] == i]
        results = pd.concat([results, row], ignore_index=True)
    else:
        #take the row from full_dataset
        row = full_dataset.loc[full_dataset['ingredient'] == i]
        results = pd.concat([results, row], ignore_index=True)

results.to_csv('datasetUtilities\\data\\ingredients_work_in_progress\\5_full_integrated_ingredient_dataset\\full_integrated_ingredient_dataset.csv', index=False)

print('Integration done!')