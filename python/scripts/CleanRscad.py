
# Camel case all the headers
# Make the fields line up
#

import pandas as pd
import os
import numpy as np


results_dir = os.path.join(os.path.dirname(
    __file__), "../../data/raw/TOPA_notices/20200226")
df = pd.read_csv(
    '../../data/raw/TOPA_notices/20200226/Rcasd_2019.csv', encoding="latin-1")
updated_col_names = {}

# Make sure the census tract is okay

# Drop colums
# df.drop(columns=["cluster2017",
#                  'LATITUDE', 'LONGITUDE', 'M_EXACTMATCH'], inplace=True)  # 2018
# df.drop(columns=["Related_address",
#                  'cluster2017', 'LATITUDE', 'LONGITUDE', 'M_EXACTMATCH'], inplace=True)

# df.rename(columns={'x': 'X', 'y': 'Y', }, inplace=True)


# Fix decimals Sale_price, Num_units, Addr_num, M_OBS, ADDRESS_ID
# df['Addr_num'].fillna(0, inplace=True)
# df['Addr_num'] = df['Addr_num'].astype(np.int64)

df['ADDRESS_ID'].fillna(0, inplace=True)
df['ADDRESS_ID'] = df['ADDRESS_ID'].astype(np.int64)
df['M_OBS'].fillna(0, inplace=True)
df['M_OBS'] = df['M_OBS'].astype(np.int64)


df.to_csv(results_dir + '/Rcasd_2019.csv', encoding="latin-1", index=False)

print("Done")
