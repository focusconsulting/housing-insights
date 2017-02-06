from collections import Counter
from csv import DictReader
from os import path
from argparse import ArgumentParser
from DataWriter import DataWriter
from Cleaner import Cleaner


class DataReader(object):
    """
    Container object that will call read in csvs and marshal them to a Postgres Database.
    """
    def __init__(self, path):
        self.path = path
        self._length = None
        self._keys = None

    def __iter__(self):
        self._length = 0
        self._counter = Counter()
        with open(self.path, 'rU') as data:
            reader = DictReader(data)
            self._keys = reader.fieldnames
            for row in reader:
                self._length += 1
                yield row

    def __len__(self):
        if self._length is None:
            for row in self:
                # Read data for length and counter
                continue
        return self._length

    @property
    def items(self):
        return self.counter.keys()

    @property
    def keys(self):
        _it = iter(self)
        next(_it)
        return self._keys

    def reset(self):
        """
        In case it breaks in the middle of reading the file
        :return:
        """
        self._length = None

if __name__ == "__main__":
    parser = ArgumentParser(description='Process some data')
    parser.add_argument('source', help='The location of the source file')
    arguments = parser.parse_args()
    if arguments.source:
        clean_type = path.split(arguments.source)[1].split('.')[0].lower()
        cleaner = Cleaner()
        reader = DataReader(arguments.source)
        clean_file = "clean_{}".format(path.split(arguments.source)[1])
        dirty_file = "dirty_{}".format(path.split(arguments.source)[1])
        header = reader.keys

        # Create writers...
        writer = DataWriter(clean_file, dirty_file, header)

        # Loop through rows..
        for row in reader:
            disposition, row = cleaner.clean(clean_type, row)
            writer.write_row(row, disposition)

        # Close handles to clean and dirty files
        writer.save()
        print("Finished reading file: {}".format(arguments.source))
        print("Data Reader: {} rows ingested".format(len(reader)))
