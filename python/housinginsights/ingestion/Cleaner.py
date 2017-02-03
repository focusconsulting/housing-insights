# Dispositions for a row
CLEAN, DIRTY, DROP = range(3)


class Cleaner(object):
    """
    A cleaner object for csv files
    """

    def __init__(self, row):
        self.row = row

    def clean(self):
        pass

    def clean_parcel_row(self):
        # There should be twelve keys
        if len(self.row) is not 12:
            print("Missing column(s) in row: {}".format(self.row))
            return DIRTY, self.row
        return CLEAN, self.row

        # TODO
        # Will need more heuristics on what we expect we will encounter and will need to be cleaned.
