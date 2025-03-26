import os, sys

# This first if __name__ is needed if this file is test-run from the command line.
# path.append needs to happen before the first from import statement
if __name__ == "__main__":
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    )


from housinginsights.sources.base_project import ProjectBaseApiConn
from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="sources.log")


class PrescatApiConn(ProjectBaseApiConn):
    """
    A little bit misnamed, the PrescatApiConn gets the flat file
    from wherever it is stored and applies transformations and data
    validation that is computationally intensive and that we
    don't want to do during the cleaning step.

    In the future, this will be have more like an ApiConn when it
    goes to fetch newly uploaded flatfiles from some online
    storage location that admins can put prescat files
    """

    def __init__(self, baseurl=None, proxies=None, database_choice=None, debug=False):

        if baseurl == None:
            baseurl = os.path.abspath(
                "../../../data/raw/preservation_catalog/20170724/Project.csv"
            )

        super().__init__(
            baseurl=baseurl,
            proxies=proxies,
            database_choice=database_choice,
            debug=debug,
        )

        self._available_unique_data_ids = ["prescat"]

    def get_data(self, unique_data_ids=None, sample=False, output_type="csv", **kwargs):
        """ """
        if unique_data_ids is None:
            unique_data_ids = self._available_unique_data_ids

        for uid in unique_data_ids:
            if uid not in self._available_unique_data_ids:
                logger.info(
                    "  The unique_data_id '{}' is not supported by the PrescatApiConn".format(
                        uid
                    )
                )
            else:
                uid = self._available_unique_data_ids[0]  # only one!

                folder = os.path.dirname(self.output_paths[uid])
                addre_path = os.path.join(folder, "{}_addre.csv".format(uid))

                # This is no longer used because we now have the proj_addre table from the prescat directly.
                # TODO remove this when confirmed that it is no longer needed.
                # self.create_address_csv_prescat(uid,proj_path=self.baseurl, addre_path=addre_path)


if __name__ == "__main__":

    pres = PrescatApiConn()
    pres.get_data()
