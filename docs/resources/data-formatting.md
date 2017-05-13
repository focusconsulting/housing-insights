---
layout: main
title: Data Formatting
---

# Data Formatting

We use the following conventions so that similar fields are formatted the same across all data sources:

`column_name` indicates the column name that should be used for this data type across all tables.

## Geographical Data

1) `ward` should contain text in the format 'Ward 1'
2) `latitude` and `longitude`
3) `anc`
4) `zip` should be a text string with only the 5 digits of the zip code
5) `neighborhood_cluster` should have the cluster by number i.e. "Cluster 1". `neighborhood_cluster_desc` should contain the long-form cluster name e.g. 'NoMa, Union Station, Stanton Park, Kingman Park'
6) `census_tract` should use the long version of the census tract code, e.g. '11001000100'
7) `ssl` for square suffix lot