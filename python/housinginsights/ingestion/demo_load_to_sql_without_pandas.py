import csv

'''
Use hard-coded data like file = filename.csv or meta = {hardcoded_meta_for_one_table} to test out how to append data to a SQL table
without using pandas_dataframe.to_sql().

Options:
 - load csv into Pandas, do type conversion and data cleaning like replacing 'NA_string' with None, and then convert to a numpy array (using .to_matrix) to load into SQL
 - use csv.DictReader and then some other tool to put the dictionary into SQL (note, don't use row-by-row INSERT, this is what causes it to be slow)
 - some other tool?

 '''

SOURCE = 'test_data/Parcel.csv'


## Return a generator to iterate over the data. Only need
## to read file once. Data is lazily evaluated, file is not opened
## read or parsed until needed. No more than one row of the file is
## in memory at any given time.
def read_souce_file(source):
    with open(source, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            yield row


if __name__ == "__main__":
    for index, row in enumerate(read_souce_file(SOURCE)):
        print "Row: {}".format(row)