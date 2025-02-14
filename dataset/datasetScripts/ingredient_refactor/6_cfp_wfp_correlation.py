
import pandas as pd
import numpy as np

df = pd.read_csv('datasetUtilities\\data\\ingredients_work_in_progress\\5_full_integrated_ingredient_dataset\\full_integrated_ingredient_dataset.csv')

#print the first row
print(df.head(1))

#drop rows where mapped_item is equal to NO_MATCH, NOT_FOOD, and NO_DATA
df = df[df['mapped_item'] != 'NO_MATCH']
df = df[df['mapped_item'] != 'NOT_FOOD']
df = df[df['mapped_item'] != 'NO_DATA']

#drop rows where wfp is null
df = df.dropna(subset=['wfp'])

cfp = df['cfp']
wfp = df['wfp']

#convert the columns to numeric, the comma is used to marcate the decimal point
cfp = pd.to_numeric(cfp.str.replace(',', '.'))
wfp = pd.to_numeric(wfp.str.replace(',', '.'))

#calculate the spearman correlation between the two columns
print(cfp)
print(wfp)

correlation = cfp.corr(wfp, method='spearman')

#print the correlation
print(correlation)
#0.523

#this correlation is not very high, but it is not low either. It is a moderate correlation.