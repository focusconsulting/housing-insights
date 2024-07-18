# Camel case all the headers
# Make the fields line up
#

import pandas as pd
import os
import numpy as np


def createProperHeader(header):
    return header.replace("_", " ").title().replace(" ", "_")


results_dir = os.path.join(
    os.path.dirname(__file__), "../../data/raw/preservation_catalog/20240709"
)
df = pd.read_csv(
    "../../data/raw/preservation_catalog/20240301/Real_property.csv",
    encoding="windows-1252",
)
updated_col_names = {}
df.replace(to_replace="U", value="01/01/1970", inplace=True)
df.replace(to_replace="N", value="01/01/1970", inplace=True)


df.to_csv(results_dir + "/Real_property.csv", encoding="utf-8", index=False)

print("Done")
