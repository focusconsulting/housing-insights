from csv import DictWriter
import os

class DataWriter(object):
    """
    Class that will handle writing out the clean and dirty csv files
    """
    def __init__(self, clean_file, dirty_file, fieldnames):
        _root = os.getcwd()
        self._clean_file = open(os.path.join(_root, clean_file), 'w')
        self._dirty_file = open(os.path.join(_root, dirty_file), 'w')

        self._clean_writer = DictWriter(self._clean_file, fieldnames=fieldnames)
        self._dirty_writer = DictWriter(self._dirty_file, fieldnames=fieldnames)

        # Write the header for both files
        self._clean_writer.writeheader()
        self._dirty_writer.writeheader()

    def write_row(self, row, disposition):
        """
        Write a row to csv file
        :param row: dictionary row to be written
        :param disposition which csv file to write to
        """
        if disposition == 'CLEAN':
            self._clean_writer.writerow(row)
        elif disposition == 'DIRTY':
            self._dirty_writer.writerow(row)
        else:
            print("Can't determine disposition of row")

    def save(self):
        self._clean_file.close()
        self._dirty_file.close()