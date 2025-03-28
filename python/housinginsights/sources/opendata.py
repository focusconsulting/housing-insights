import sys, os

# This first if __name__ is needed if this file is test-run from the command line.
# path.append needs to happen before the first from import statement
if __name__ == "__main__":
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    )


from housinginsights.sources.base import BaseApiConn
from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="sources.log")


class OpenDataApiConn(BaseApiConn):
    """ """

    def __init__(self, baseurl=None, proxies=None, database_choice=None, debug=False):
        # baseurl not actually used since we need the _urls property to hold many urls.
        # Needed to get call to super() to work correctly. TODO refactor so this is optional.
        baseurl = "https://opendata.arcgis.com/datasets/"
        super(OpenDataApiConn, self).__init__(
            baseurl=baseurl, proxies=proxies, debug=debug
        )

        self._available_unique_data_ids = [
            "tax",
            "building_permits_2013",
            "building_permits_2014",
            "building_permits_2015",
            "building_permits_2016",
            "building_permits_2017",
            "building_permits_2018",
            "building_permits_2019",
            "building_permits_2020",
            "building_permits_2021",
            "building_permits_2022",
            "building_permits_2023",
            "crime_2013",
            "crime_2014",
            "crime_2015",
            "crime_2016",
            "crime_2017",
            "crime_2018",
            "crime_2019",
            "crime_2020",
            "crime_2021",
            "crime_2022",
            "crime_2023",
            "mar",
        ]

        self._urls = {
            # "tax": "014f4b4f94ea461498bfeba877d92319_56.csv",
            "tax": "f4af92a9bba84bf0942a64fe7ada33fe_0.csv",
            "building_permits_2013": "4911fcf3527246ae9bf81b5553a48c4d_6.csv",
            "building_permits_2014": "d4891ca6951947538f6707a6b07ae225_5.csv",
            "building_permits_2015": "981c105beef74af38cc4090992661264_25.csv",
            "building_permits_2016": "5d14ae7dcd1544878c54e61edda489c3_24.csv",
            "building_permits_2017": "81a359c031464c53af6230338dbc848e_37.csv",
            "building_permits_2018": "42cbd10c2d6848858374facb06135970_9.csv",
            "building_permits_2019": "52e671890cb445eba9023313b1a85804_8.csv",
            "building_permits_2020": "066cda75c1754a088e821baa1cf8ac18_2.csv",
            "building_permits_2021": "fea4cae3ae1f41beb5531ecf2ef5efc3_3.csv",
            "building_permits_2022": "972618416ec14a9c91c77f9730a4461d_14.csv",
            "building_permits_2023": "6a809af9bfa14567b383edbc7f07e5b7_15.csv",
            "crime_2013": "5fa2e43557f7484d89aac9e1e76158c9_10.csv",
            "crime_2014": "6eaf3e9713de44d3aa103622d51053b5_9.csv",
            "crime_2015": "35034fcb3b36499c84c94c069ab1a966_27.csv",
            "crime_2016": "bda20763840448b58f8383bae800a843_26.csv",
            "crime_2017": "6af5cb8dc38e4bcbac8168b27ee104aa_38.csv",
            "crime_2018": "38ba41dd74354563bce28a359b59324e_0.csv",
            "crime_2019": "f08294e5286141c293e9202fcd3e8b57_1.csv",
            "crime_2020": "f516e0dd7b614b088ad781b0c4002331_2.csv",
            "crime_2021": "619c5bd17ca2411db0689bb0a211783c_3.csv",
            "crime_2022": "f9cc541fc8c04106a05a1a4f1e7e813c_4.csv",
            "crime_2023": "89561a4f02ba46cca3c42333425d1b87_5.csv",
            "mar": "aa514416aaf74fdc94748f1e56e7cc8a_0.csv",
        }

    def get_data(self, unique_data_ids=None, sample=False, output_type="csv", **kwargs):
        """
        Gets all data sources associated with this ApiConn class.

        sample does not apply to this apiconn object because api doesn't let us request only some data.
        """
        if unique_data_ids == None:
            unique_data_ids = self._available_unique_data_ids

        for u in unique_data_ids:
            if u not in self._available_unique_data_ids:
                # TODO Change this error type to a more specific one that should be handled by calling function inproduction
                # We will want the calling function to continue with other data sources instead of erroring out.
                logger.info(
                    "  The unique_data_id '%s' is not supported by the OpenDataApiConn",
                    u,
                )
            else:
                result = self.get(self._urls[u], params=None)

                if result.status_code != 200:
                    err = "An error occurred during request: status {0}"
                    logger.exception(err.format(result.status_code))
                    continue
                result.encoding = "utf-8"
                content = result.text

                if output_type == "stdout":
                    print(content)

                elif output_type == "csv":
                    self.directly_to_file(content, self.output_paths[u])

                # Can't yield content if we get multiple sources at once
                if len(unique_data_ids) == 1:
                    return content


if __name__ == "__main__":

    api_conn = OpenDataApiConn()
    unique_data_ids = None  # ['crime_2013']
    api_conn.get_data(unique_data_ids)
