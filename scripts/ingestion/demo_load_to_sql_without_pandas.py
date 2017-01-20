
import csv
import argparse
'''
Use hard-coded data like file = filename.csv or meta = {hardcoded_meta_for_one_table} to test out how to append data to a SQL table
without using pandas_dataframe.to_sql().

Options:
 - load csv into Pandas, do type conversion and data cleaning like replacing 'NA_string' with None, and then convert to a numpy array (using .to_matrix) to load into SQL
 - use csv.DictReader and then some other tool to put the dictionary into SQL (note, don't use row-by-row INSERT, this is what causes it to be slow)
 - some other tool?

 '''
CLEAN, DIRTY, DROP = range(3)

def clean_row(row):
    """
    Return a pair (state, row) if:
    `CLEAN` if `row` was succesfully cleaned
    `DIRTY` if `row` could not be cleaned
    `DROP`  if `row` was empty.
    """
    # Sanitize data
    for idx, field in enumerate(row):
        print idx, field
        if field == 'NA_string':
            row[idx] = ''
    print row
    return CLEAN, row


def clean_csv(input_file, clean, dirty):
    """
    Read rows from the csv file. Clean rows are written to a
    clean output file and dirty rows are written to a dirty
    output file.
    """
    clean_writer = csv.writer(clean)
    dirty_writer = csv.writer(dirty)
    headings = "street_address, city, latitude, longitude".split(',')
    for writer in clean_writer, dirty_writer:
        writer.writerow(headings)

    # Start processing rows
    for row in csv.reader(input_file):
        disposition, row = clean_row(row)
        if disposition == CLEAN:
            clean_writer.writerow(row)
        elif disposition == DIRTY:
            dirty_writer.writerow(row)
        else:
            assert disposition == DROP

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description=clean_csv.__doc__)
    PARSER.add_argument('INPUT', type=argparse.FileType('r'), help='Input CSV file')
    PARSER.add_argument('CLEAN', type=argparse.FileType('w'), help='Clean output file')
    PARSER.add_argument('DIRTY', type=argparse.FileType('w'), help='Dirty output file')
    ARGUMENTS = PARSER.parse_args()
    clean_csv(ARGUMENTS.INPUT, ARGUMENTS.CLEAN, ARGUMENTS.DIRTY)
