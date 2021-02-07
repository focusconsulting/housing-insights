
# Camel case all the headers
# Make the fields line up
#

import pandas as pd
import os
import numpy as np


def createProperHeader(header):
    return header.replace('_', ' ').title().replace(' ', '_')


results_dir = os.path.join(os.path.dirname(
    __file__), "../../data/raw/preservation_catalog/20210206")
df = pd.read_csv('../../data/raw/preservation_catalog/20210206/Reac_score.csv')
updated_col_names = {}
# Drop colums
if 'REAC_ID' in df.columns:
    df.drop(columns=['REAC_ID'], inplace=True)


df.to_csv(results_dir + '/Reac_score.csv', encoding="utf-8", index=False)

print("Done")
