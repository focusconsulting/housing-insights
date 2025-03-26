# Camel case all the headers
# Make the fields line up
#

import pandas as pd
import os
import numpy as np


def createProperHeader(header):
    return header.replace("_", " ").title().replace(" ", "_")


results_dir = os.path.join(
    os.path.dirname(__file__), "../../data/raw/preservation_catalog/20220620"
)
df = pd.read_csv("../../data/raw/preservation_catalog/20220620/Reac_score.csv")
updated_col_names = {}
# Drop colums
if "REAC_id" in df.columns:
    df.drop(columns=["REAC_id"], inplace=True)

if "reac_inspec_id" in df.columns:
    df.drop(columns=["reac_inspec_id"], inplace=True)

df.rename(
    columns={
        "nlihc_id": "Nlihc_id",
        "reac_score": "REAC_score",
        "reac_date": "REAC_date",
        "reac_score_num": "REAC_score_num",
        "reac_score_letter": "REAC_score_letter",
        "reac_score_star": "REAC_score_star",
    },
    inplace=True,
)

df.to_csv(results_dir + "/Reac_score.csv", encoding="utf-8", index=False)

print("Done")
