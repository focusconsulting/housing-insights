#Needed to make relative package imports when running this file as a script (i.e. for testing purposes). Read why here: https://www.blog.pythonlibrary.org/2016/03/01/python-101-all-about-imports/
if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.abspath('../../'))

#Relative package imports
from housinginsights.tools import database
from housinginsights.ingestion.DataReader import ManifestReader, DataReader
from housinginsights.ingestion.load_data import load_meta_data





if __name__ == '__main__':
	

	mr = ManifestReader()
	print(mr.path)

	print(mr.has_unique_ids())


