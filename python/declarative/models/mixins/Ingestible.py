import os
from shutil import copyfile
from csv import DictReader

class Ingestible():
    LOCAL_FOLDER = "../../data"
    S3_FOLDER = "https://s3.amazonaws.com/housinginsights/"
    ROW_OFFSET = 0
    
    @classmethod
    def load_local_file(cls, file_path):
        path = os.path.join(cls.LOCAL_FOLDER, file_path)
        with open(path, 'r', newline='', encoding='latin-1') as data:
            reader = DictReader(data)
            reader.fieldnames = [name.replace('.', '_') for name in reader.fieldnames]
            for rownum, row in enumerate(reader):
                if True: #rownum >= cls.ROW_OFFSET:  # Better way?
                    yield row

    @classmethod
    def copy_s3_to_local_file(cls, file_path):
        copyfile(
            os.path.join(cls.S3_FOLDER, file_path),
            os.path.join(cls.LOCAL_FOLDER, file_path)
        )

    @classmethod
    def load_file(cls, file_path, force_local=False):
        local_path = os.path.join(cls.LOCAL_FOLDER, file_path)
        s3_path = os.path.join(cls.S3_FOLDER, file_path)

        if os.path.isfile(local_path):
            for row in cls.load_local_file(file_path):
                yield row
        elif not force_local:
            cls.copy_s3_to_local_file(file_path)
            for row in self.load_local_file(file_path):
                yield row
        else:
            raise FileNotFoundError("Could not find {}. You may want to try without force_local.".format(path))

    @classmethod
    def load_data(cls, force_local=False):
        for row in cls.load_file(cls.FILE_PATH, force_local=force_local):
            yield row


class MultipleFileIngestible(Ingestible):
    
    @classmethod
    def load_data(cls, force_local=False):
        # There may be a more elegant way to do this, but for example:
        for year, file_path in zip(cls.YEAR_RANGE, cls.get_file_paths()):
            for row in cls.load_file(file_path, force_local=force_local):
                row[cls.YEAR_RANGE_FIELD] = year
                yield row
