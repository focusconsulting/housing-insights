
# Camel case all the headers
# Make the fields line up
#

import pandas as pd
import os
import numpy as np


def createProperHeader(header):
    return header.replace('_', ' ').title().replace(' ', '_')


results_dir = os.path.join(os.path.dirname(
    __file__), "../../data/raw/preservation_catalog/20191205")
df = pd.read_csv('../../data/raw/preservation_catalog/20191205/Project.csv')
updated_col_names = {}
# Make sure the column names are correct
for col in df.columns:
    updated_col_names[col] = createProperHeader(col)
# Make sure the census tract is okay
for index, value in df['Geo2010'].items():
    df.at[index, 'Geo2010'] = value.replace('DC ', '')
# Drop colums
# df.drop(columns=['Added_To_Catalog'], inplace=True)
# print(df['Proj_address_id'])
df['Proj_address_id'].fillna(0, inplace=True)
df['Proj_address_id'] = df['Proj_address_id'].astype(np.int64)
df['Proj_ayb'].fillna(0, inplace=True)
df['Proj_ayb'] = df['Proj_ayb'].astype(np.int64)
df['Proj_eyb'].fillna(0, inplace=True)
df['Proj_eyb'] = df['Proj_eyb'].astype(np.int64)

df.to_csv(results_dir + '/Project.csv', encoding="utf-8", index=False)

print("Done")
