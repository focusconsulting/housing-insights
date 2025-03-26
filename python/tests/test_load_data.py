import unittest
import os
from python.housinginsights.ingestion import LoadData as load_data
from sqlalchemy.exc import ProgrammingError

PYTHON_PATH = load_data.PYTHON_PATH


class MyTestCase(unittest.TestCase):
    def setUp(self):
        # use test data
        test_data_path = os.path.abspath(
            os.path.join(PYTHON_PATH, "tests", "test_data")
        )
        self.meta_path = os.path.abspath(
            os.path.join(test_data_path, "meta_load_data.json")
        )
        self.manifest_path = os.path.abspath(
            os.path.join(test_data_path, "manifest_load_data.csv")
        )
        self.database_choice = "docker_database"
        self.loader = load_data.LoadData(
            database_choice=self.database_choice,
            meta_path=self.meta_path,
            manifest_path=self.manifest_path,
        )

    def query_db(self, engine, query):
        """
        Helper function that returns the result of querying the database.
        """
        try:
            query_result = engine.execute(query)
            return [dict(x) for x in query_result.fetchall()]
        except ProgrammingError as e:
            self.assertEqual(True, False, e)

    def test_update_only(self):
        # use the same sql engine for db lookup
        loader_engine = self.loader.engine

        # start with empty database
        self.loader._drop_tables()
        result = loader_engine.table_names()
        self.assertEqual(len(result), 0)

        # load crime data one at a time without overriding
        # existing data
        crime_data = ["crime_2016", "crime_2015", "crime_2017"]
        table_name = "crime"

        for idx, data_id in enumerate(crime_data, start=1):
            these_data = [data_id]
            result = self.loader.update_database(unique_data_id_list=these_data)
            self.assertTrue(data_id in result)

            # validate database contents
            query = "SELECT DISTINCT unique_data_id FROM crime"
            results = self.query_db(loader_engine, query)

            self.assertEqual(len(results), idx)

            for result in results:
                self.assertTrue(result["unique_data_id"] in crime_data)

        # there's only 'crime' and manifest table in database
        result = loader_engine.table_names()
        self.assertEqual(len(result), 2)
        self.assertTrue(table_name in result)
        self.assertTrue("manifest" in result)

        # make sure database is not empty
        self.loader.rebuild()
        result = loader_engine.table_names()
        self.assertTrue(len(result) > 0)

        # update sample of data_ids and make sure no duplications
        these_data = ["project", "crime_2017", "dchousing_subsidy"]

        # get current table and unique_data_id row counts
        tables = ["project", "crime", "subsidy"]
        tables_row_counts = []
        data_id_row_counts = []

        for idx, table in enumerate(tables):
            # get table counts
            query = "SELECT COUNT(*) FROM {}".format(table)
            result = self.query_db(loader_engine, query)
            tables_row_counts.append(result[0]["count"])

            # get unique_data_id counts
            query = "SELECT COUNT(*) FROM {} WHERE unique_data_id = " "'{}'".format(
                table, these_data[idx]
            )
            result = self.query_db(loader_engine, query)
            data_id_row_counts.append(result[0]["count"])

        processed_data_id = self.loader.update_database(these_data)

        for data_id in these_data:
            self.assertTrue(data_id in processed_data_id)

        for idx, table in enumerate(tables):
            # get updated table counts
            query = "SELECT COUNT(*) FROM {}".format(table)
            result = self.query_db(loader_engine, query)
            self.assertEqual(result[0]["count"], tables_row_counts[idx])

            # get updated unique_data_id counts
            query = "SELECT COUNT(*) FROM {} WHERE unique_data_id = " "'{}'".format(
                table, these_data[idx]
            )
            result = self.query_db(loader_engine, query)
            self.assertEqual(result[0]["count"], data_id_row_counts[idx])

    def test_create_list(self):
        # Note - you will need to modify folder path to match local env
        folder_path = os.path.join(
            PYTHON_PATH, os.pardir, "data", "raw", "apis", "20170528"
        )
        result = self.loader.create_list(folder_path)
        print(result)
        self.assertEqual(len(result), 13)

    def test_rebuild(self):
        result = self.loader.rebuild()
        self.assertTrue(result)

    def test_make_manifest(self):
        folder_path = os.path.join(PYTHON_PATH, os.pardir, "data", "raw", "apis")
        fields = self.loader.manifest.keys
        print(fields)
        self.assertTrue(fields)
        result_path = self.loader.make_manifest(folder_path)
        self.assertEqual(self.loader.manifest.path, result_path)

    def test__get_zone_fact_zones(self):
        ward_types = self.loader._get_zone_specifics_for_zone_type("ward")

        for idx in range(1, 9):
            ward = "Ward " + str(idx)
            self.assertTrue(ward in ward_types)

    def test__create_zone_facts_table(self):
        # make sure zone_facts is not in db
        if "zone_facts" in self.loader.engine.table_names():
            with self.loader.engine.connect() as conn:
                conn.execute("DROP TABLE zone_facts;")

        # currently no zone_facts table
        result = "zone_facts" in self.loader.engine.table_names()
        self.assertFalse(result, "zone_facts table is not in db")

        # # check returned metadata.tables contains 'zone_facts' table
        # result = self.loader._create_zone_facts_table().keys()
        # self.assertTrue('zone_facts' in result, 'zone_facts is in '
        #                                         'metadata.tables object')

        # create zone_facts table
        self.loader._create_zone_facts_table()

        # confirm zone_facts table was loaded into db
        result = "zone_facts" in self.loader.engine.table_names()
        self.assertTrue(result, "zone_facts table is in db")

    def test__get_weighted_census_results(self):
        """SQL Code used to validate results:

        -- validate acs_lower_rent_quartile calculations
        select round(sum(population_weight_proportions * acs_lower_rent_quartile)) as val
        from census_tract_to_neighborhood_cluster as ctn, census where ctn.neighborhood_cluster = 'Cluster 33'
        and census.census_tract = ctn.census_tract;

        -- validate acs_median_rent calculations
        select round(sum(population_weight_proportions * acs_median_rent))
        from census_tract_to_ward as ctw, census where ctw.ward = 'Ward 1' and census.census_tract = ctw.census_tract;

        -- validate aggregate_income calculations
        select round(sum(val)) / round(sum(pop)) as calc_val, round(sum(val)) as total_val,
        round(sum(pop)) as total_weight from (
          select ctn.census_tract, population_weight_counts * aggregate_income as val,
          population_weight_counts * population as pop, population
          from census_tract_to_neighborhood_cluster as ctn, census where ctn.neighborhood_cluster = 'Cluster 4'
          and census.census_tract = ctn.census_tract) as result;

        -- validate population_black calculations
        select round(sum(val)) / round(sum(pop)) as calc_val, round(sum(val)) as total_val,
        round(sum(pop)) as total_weight from (
          select ctw.census_tract, population_weight_counts * population_black as val,
          population_weight_counts * population as pop, population
          from census_tract_to_ward as ctw, census where ctw.ward = 'Ward 1' and census.census_tract = ctw.census_tract) as result;
        """
        # expected calculated results for test cases
        poverty_rate_census_tract = {
            "items": [
                {"count": 0.01682496607869742, "group": "11001000201"},
                {"count": 0.18268631928586257, "group": "11001000202"},
                {"count": 0.15438884331419195, "group": "11001000300"},
                {"count": 0.09885931558935361, "group": "11001000400"},
                {"count": 0.06310679611650485, "group": "11001000501"},
                {"count": 0.02119071644803229, "group": "11001000502"},
                {"count": 0.08470986869970351, "group": "11001000600"},
                {"count": 0.09876072449952336, "group": "11001000701"},
                {"count": 0.12454764776839566, "group": "11001000702"},
                {"count": 0.13125475285171104, "group": "11001000801"},
                {"count": 0.14018395179194418, "group": "11001000802"},
                {"count": 0.0649550706033376, "group": "11001000901"},
                {"count": 0.017107942973523423, "group": "11001000902"},
                {"count": 0.04484418545730935, "group": "11001001001"},
                {"count": 0.28309979982842437, "group": "11001001002"},
                {"count": 0.03923603902844094, "group": "11001001100"},
                {"count": 0.051548492257538714, "group": "11001001200"},
                {"count": 0.06200199203187251, "group": "11001001301"},
                {"count": 0.10841786325912264, "group": "11001001302"},
                {"count": 0.07420599584446423, "group": "11001001401"},
                {"count": 0.09645432692307693, "group": "11001001402"},
                {"count": 0.01669291338582677, "group": "11001001500"},
                {"count": 0.03832335329341317, "group": "11001001600"},
                {"count": 0.08855011352578657, "group": "11001001702"},
                {"count": 0.12666996536368136, "group": "11001001803"},
                {"count": 0.1624844278341342, "group": "11001001804"},
                {"count": 0.10582937202902176, "group": "11001001901"},
                {"count": 0.08429610611895592, "group": "11001001902"},
                {"count": 0.06811797752808989, "group": "11001002001"},
                {"count": 0.13193556635131679, "group": "11001002002"},
                {"count": 0.14934289127837516, "group": "11001002101"},
                {"count": 0.17902865271286325, "group": "11001002102"},
                {"count": 0.07802375809935205, "group": "11001002201"},
                {"count": 0.26396577755410167, "group": "11001002202"},
                {"count": 0.1046583850931677, "group": "11001002301"},
                {"count": 0.19871420222092342, "group": "11001002302"},
                {"count": 0.07728447263330984, "group": "11001002400"},
                {"count": 0.22922960725075528, "group": "11001002501"},
                {"count": 0.14678742310321258, "group": "11001002502"},
                {"count": 0.05091333074232413, "group": "11001002600"},
                {"count": 0.1575165806927045, "group": "11001002701"},
                {"count": 0.0784126984126984, "group": "11001002702"},
                {"count": 0.20852963054797918, "group": "11001002801"},
                {"count": 0.1957894736842105, "group": "11001002802"},
                {"count": 0.07466608276768119, "group": "11001002900"},
                {"count": 0.26202603282399545, "group": "11001003000"},
                {"count": 0.10597014925373134, "group": "11001003100"},
                {"count": 0.16269761857114268, "group": "11001003200"},
                {"count": 0.07571152252003316, "group": "11001003301"},
                {"count": 0.12147134302822926, "group": "11001003302"},
                {"count": 0.1111111111111111, "group": "11001003400"},
                {"count": 0.11440299839371765, "group": "11001003500"},
                {"count": 0.10424940428911834, "group": "11001003600"},
                {"count": 0.16194539249146758, "group": "11001003700"},
                {"count": 0.11128999798752263, "group": "11001003800"},
                {"count": 0.09817453250222619, "group": "11001003900"},
                {"count": 0.0441747572815534, "group": "11001004001"},
                {"count": 0.03802535023348899, "group": "11001004002"},
                {"count": 0.057267125770206595, "group": "11001004100"},
                {"count": 0.048827586206896555, "group": "11001004201"},
                {"count": 0.07096774193548387, "group": "11001004202"},
                {"count": 0.11801075268817204, "group": "11001004300"},
                {"count": 0.13451420554191512, "group": "11001004400"},
                {"count": 0.13844587716321682, "group": "11001004600"},
                {"count": 0.2364895042429656, "group": "11001004701"},
                {"count": 0.13604378420641125, "group": "11001004702"},
                {"count": 0.09626630679262259, "group": "11001004801"},
                {"count": 0.25507328072153324, "group": "11001004802"},
                {"count": 0.20692307692307693, "group": "11001004901"},
                {"count": 0.12280084447572133, "group": "11001004902"},
                {"count": 0.08270321361058601, "group": "11001005001"},
                {"count": 0.13072219467856552, "group": "11001005002"},
                {"count": 0.07904884318766067, "group": "11001005201"},
                {"count": 0.07781556311262253, "group": "11001005301"},
                {"count": 0.17506031363088057, "group": "11001005500"},
                {"count": 0.16427340608845492, "group": "11001005600"},
                {"count": 0.16361021215390148, "group": "11001005800"},
                {"count": 0.12421929215822346, "group": "11001005900"},
                {"count": 0.0, "group": "11001006202"},
                {"count": 0.44272300469483566, "group": "11001006400"},
                {"count": 0.08130081300813008, "group": "11001006500"},
                {"count": 0.026260504201680673, "group": "11001006600"},
                {"count": 0.03821504865891289, "group": "11001006700"},
                {"count": 0.09866137828458106, "group": "11001006801"},
                {"count": 0.1071733561058924, "group": "11001006802"},
                {"count": 0.04035266191929467, "group": "11001006804"},
                {"count": 0.03897294818890417, "group": "11001006900"},
                {"count": 0.04294917680744453, "group": "11001007000"},
                {"count": 0.25032637075718017, "group": "11001007100"},
                {"count": 0.11387434554973822, "group": "11001007200"},
                {"count": 0.022488755622188907, "group": "11001007301"},
                {"count": 0.3841775754126352, "group": "11001007304"},
                {"count": 0.6070118222584591, "group": "11001007401"},
                {"count": 0.31657142857142856, "group": "11001007403"},
                {"count": 0.40421607378129115, "group": "11001007404"},
                {"count": 0.2992486115648481, "group": "11001007406"},
                {"count": 0.25091441111923923, "group": "11001007407"},
                {"count": 0.4447576099210823, "group": "11001007408"},
                {"count": 0.37769594950026303, "group": "11001007409"},
                {"count": 0.4974818130945719, "group": "11001007502"},
                {"count": 0.47141796585003715, "group": "11001007503"},
                {"count": 0.4784172661870504, "group": "11001007504"},
                {"count": 0.23792443806791008, "group": "11001007601"},
                {"count": 0.20734177215189872, "group": "11001007603"},
                {"count": 0.18003186404673394, "group": "11001007604"},
                {"count": 0.2876142975893599, "group": "11001007605"},
                {"count": 0.4670590468957661, "group": "11001007703"},
                {"count": 0.27424824779561385, "group": "11001007707"},
                {"count": 0.31400651465798046, "group": "11001007708"},
                {"count": 0.28729792147806005, "group": "11001007709"},
                {"count": 0.20875323927440254, "group": "11001007803"},
                {"count": 0.26944617299315493, "group": "11001007804"},
                {"count": 0.26298076923076924, "group": "11001007806"},
                {"count": 0.212618841832325, "group": "11001007807"},
                {"count": 0.2951737001632082, "group": "11001007808"},
                {"count": 0.24242424242424243, "group": "11001007809"},
                {"count": 0.2308276385725133, "group": "11001007901"},
                {"count": 0.2652054794520548, "group": "11001007903"},
                {"count": 0.06375628140703518, "group": "11001008001"},
                {"count": 0.07219402143260012, "group": "11001008002"},
                {"count": 0.017434620174346202, "group": "11001008100"},
                {"count": 0.0696483441447593, "group": "11001008200"},
                {"count": 0.03734788082249266, "group": "11001008301"},
                {"count": 0.061436280614362807, "group": "11001008302"},
                {"count": 0.10407876230661041, "group": "11001008402"},
                {"count": 0.08413284132841328, "group": "11001008410"},
                {"count": 0.10644742535698831, "group": "11001008701"},
                {"count": 0.2533678756476684, "group": "11001008702"},
                {"count": 0.25772074815137014, "group": "11001008802"},
                {"count": 0.3207635009310987, "group": "11001008803"},
                {"count": 0.2989352989352989, "group": "11001008804"},
                {"count": 0.3264069264069264, "group": "11001008903"},
                {"count": 0.24523965856861457, "group": "11001008904"},
                {"count": 0.1751393899639226, "group": "11001009000"},
                {"count": 0.276285930408472, "group": "11001009102"},
                {"count": 0.17558602388323752, "group": "11001009201"},
                {"count": 0.18529862174578868, "group": "11001009203"},
                {"count": 0.41077199281867144, "group": "11001009204"},
                {"count": 0.07927590511860175, "group": "11001009301"},
                {"count": 0.07027540360873694, "group": "11001009302"},
                {"count": 0.11835051546391752, "group": "11001009400"},
                {"count": 0.16605530474040633, "group": "11001009501"},
                {"count": 0.08664475649835673, "group": "11001009503"},
                {"count": 0.11372549019607843, "group": "11001009504"},
                {"count": 0.09626064420584969, "group": "11001009505"},
                {"count": 0.11220110361741263, "group": "11001009507"},
                {"count": 0.0770436145207626, "group": "11001009508"},
                {"count": 0.043041606886657105, "group": "11001009509"},
                {"count": 0.431026684758028, "group": "11001009601"},
                {"count": 0.4150997975122939, "group": "11001009602"},
                {"count": 0.16522893165228933, "group": "11001009603"},
                {"count": 0.09629981024667932, "group": "11001009604"},
                {"count": 0.384752299021062, "group": "11001009700"},
                {"count": 0.3895321908290875, "group": "11001009801"},
                {"count": 0.4957472660996355, "group": "11001009802"},
                {"count": 0.4526161727039883, "group": "11001009803"},
                {"count": 0.34737221022318215, "group": "11001009804"},
                {"count": 0.3259940847847519, "group": "11001009807"},
                {"count": 0.4020926756352765, "group": "11001009810"},
                {"count": 0.32841769629334394, "group": "11001009811"},
                {"count": 0.09559110417479516, "group": "11001009901"},
                {"count": 0.10971223021582734, "group": "11001009902"},
                {"count": 0.1772428884026258, "group": "11001009903"},
                {"count": 0.35093419983753044, "group": "11001009904"},
                {"count": 0.2658318425760286, "group": "11001009905"},
                {"count": 0.2695595003287311, "group": "11001009906"},
                {"count": 0.37750865051903115, "group": "11001009907"},
                {"count": 0.12842987804878048, "group": "11001010100"},
                {"count": 0.06937327552227039, "group": "11001010200"},
                {"count": 0.19699595609474294, "group": "11001010300"},
                {"count": 0.2901206973625391, "group": "11001010400"},
                {"count": 0.12170860152135751, "group": "11001010500"},
                {"count": 0.15320767767594673, "group": "11001010600"},
                {"count": 0.1900054914881933, "group": "11001010700"},
                {"count": 0.08475115280648751, "group": "11001010800"},
                {"count": 0.4816374269005848, "group": "11001010900"},
                {"count": 0.03575450450450451, "group": "11001011000"},
                {"count": 0.19781420765027322, "group": "11001011100"},
            ]
        }
        fraction_black_ward = {
            "items": [
                {"count": 0.92742512017749291261, "group": "Ward 8"},
                {"count": 0.56325958242443128701, "group": "Ward 4"},
                {"count": 0.35139036800378653414, "group": "Ward 6"},
                {"count": 0.06884871735725819180, "group": "Ward 3"},
                {"count": 0.70208090520590520591, "group": "Ward 5"},
                {"count": 0.08835013166258058658, "group": "Ward 2"},
                {"count": 0.94173206851839213813, "group": "Ward 7"},
                {"count": 0.30254329848650335466, "group": "Ward 1"},
            ]
        }
        income_per_capita_cluster = {
            "items": [
                {"count": 14491.2609749528683006, "group": "Cluster 38"},
                {"count": 19264.256563732825, "group": "Cluster 31"},
                {"count": 75794.728760226558, "group": "Cluster 11"},
                {"count": 17215.367965367965, "group": "Cluster 30"},
                {"count": 86761.24080845013203331302052, "group": "Cluster 13"},
                {"count": 63782.37384783627558194032182, "group": "Cluster 7"},
                {"count": 32857.73716951788491446345257, "group": "Cluster 35"},
                {"count": 28624.43163960188580408590885, "group": "Cluster 22"},
                {"count": 16034.49932897915361903909815, "group": "Cluster 39"},
                {"count": 65440.64721614393386822270849, "group": "Cluster 14"},
                {"count": 46749.08070478068013799901429, "group": "Cluster 5"},
                {"count": 80231.58883949103173386478614, "group": "Cluster 10"},
                {"count": 71543.66015099803495707932568, "group": "Cluster 1"},
                {"count": 51515.86035564853556485355649, "group": "Cluster 27"},
                {"count": 54680.58086212167532864567411, "group": "Cluster 25"},
                {"count": 32510.86035281363949935941658, "group": "Cluster 20"},
                {"count": 35525.07201915522466235175278, "group": "Cluster 2"},
                {"count": 61387.13192215773301468077842, "group": "Cluster 8"},
                {"count": 54246.68729053879865944831142, "group": "Cluster 9"},
                {"count": 22698.76713227096858810413798, "group": "Cluster 19"},
                {"count": 75409.98802395209580838323353, "group": "Cluster 16"},
                {"count": 21677.23421874004713676030320, "group": "Cluster 23"},
                {"count": 70922.649702110472, "group": "Cluster 4"},
                {"count": 84103.38887518500246669955599, "group": "Cluster 12"},
                {"count": 80583.69066528545119705340700, "group": "Cluster 6"},
                {"count": 54934.72909888244447588060546, "group": "Cluster 3"},
                {"count": 15129.89597467209407507914971, "group": "Cluster 29"},
                {"count": 31335.93088213269432379811292, "group": "Cluster 24"},
                {"count": 100253.5678445770230992810158, "group": "Cluster 15"},
                {"count": 36192.01224666986542372106838, "group": "Cluster 18"},
                {"count": 38881.72378983800413401913186, "group": "Cluster 21"},
                {"count": 14006.08330288637194008037998, "group": "Cluster 28"},
                {"count": 31788.91811862417622099846529, "group": "Cluster 17"},
                {"count": 59333.57003288376304627555640, "group": "Cluster 26"},
                {"count": 13317.66599258510279743849006, "group": "Cluster 36"},
                {"count": 13865.81334786821705426356589, "group": "Cluster 37"},
                {"count": 22876.96428571428571428571429, "group": "Non-cluster area"},
                {"count": 25510.01372638734557814236225, "group": "Cluster 34"},
                {"count": 20444.54268519206478936027937, "group": "Cluster 32"},
                {"count": 19800.75381619448457817702117, "group": "Cluster 33"},
            ]
        }

        # expected proportion results for test cases
        lower_rent_cluster = {
            "items": [
                {"count": 531, "group": "Cluster 38"},
                {"count": 480, "group": "Cluster 31"},
                {"count": 1308, "group": "Cluster 11"},
                {"count": 513, "group": "Cluster 30"},
                {"count": 1561, "group": "Cluster 13"},
                {"count": 958, "group": "Cluster 7"},
                {"count": 752, "group": "Cluster 35"},
                {"count": 615, "group": "Cluster 22"},
                {"count": 540, "group": "Cluster 39"},
                {"count": 1318, "group": "Cluster 14"},
                {"count": 1455, "group": "Cluster 5"},
                {"count": 2273, "group": "Cluster 10"},
                {"count": 1332, "group": "Cluster 1"},
                {"count": 924, "group": "Cluster 27"},
                {"count": 1169, "group": "Cluster 25"},
                {"count": 874, "group": "Cluster 20"},
                {"count": 798, "group": "Cluster 2"},
                {"count": 1130, "group": "Cluster 8"},
                {"count": 1068, "group": "Cluster 9"},
                {"count": 822, "group": "Cluster 19"},
                {"count": 825, "group": "Cluster 16"},
                {"count": 622, "group": "Cluster 23"},
                {"count": 1246, "group": "Cluster 4"},
                {"count": 1446, "group": "Cluster 12"},
                {"count": 1446, "group": "Cluster 6"},
                {"count": 848, "group": "Cluster 3"},
                {"count": 280, "group": "Cluster 29"},
                {"count": 482, "group": "Cluster 24"},
                {"count": 1438, "group": "Cluster 15"},
                {"count": 659, "group": "Cluster 18"},
                {"count": 659, "group": "Cluster 21"},
                {"count": 387, "group": "Cluster 28"},
                {"count": 922, "group": "Cluster 17"},
                {"count": 940, "group": "Cluster 26"},
                {"count": 430, "group": "Cluster 36"},
                {"count": 675, "group": "Cluster 37"},
                {"count": 1520, "group": "Non-cluster area"},
                {"count": 631, "group": "Cluster 34"},
                {"count": 603, "group": "Cluster 32"},
                {"count": 498, "group": "Cluster 33"},
            ]
        }
        median_rent_ward = {
            "items": [
                {"count": 896, "group": "Ward 8"},
                {"count": 1272, "group": "Ward 4"},
                {"count": 1432, "group": "Ward 6"},
                {"count": 1911, "group": "Ward 3"},
                {"count": 1093, "group": "Ward 5"},
                {"count": 1739, "group": "Ward 2"},
                {"count": 756, "group": "Ward 7"},
                {"count": 1344, "group": "Ward 1"},
            ]
        }
        upper_rent_census_tract = {
            "items": [
                {"count": None, "group": "11001000201"},
                {"count": 3501, "group": "11001000202"},
                {"count": 2187, "group": "11001000300"},
                {"count": 2661, "group": "11001000400"},
                {"count": 2242, "group": "11001000501"},
                {"count": 1931, "group": "11001000502"},
                {"count": 2297, "group": "11001000600"},
                {"count": 1917, "group": "11001000701"},
                {"count": 1884, "group": "11001000702"},
                {"count": 2453, "group": "11001000801"},
                {"count": 1965, "group": "11001000802"},
                {"count": 3501, "group": "11001000901"},
                {"count": 3350, "group": "11001000902"},
                {"count": 3336, "group": "11001001001"},
                {"count": 2262, "group": "11001001002"},
                {"count": 2099, "group": "11001001100"},
                {"count": 1976, "group": "11001001200"},
                {"count": 2348, "group": "11001001301"},
                {"count": 2229, "group": "11001001302"},
                {"count": 1901, "group": "11001001401"},
                {"count": 2367, "group": "11001001402"},
                {"count": 3501, "group": "11001001500"},
                {"count": None, "group": "11001001600"},
                {"count": 2251, "group": "11001001702"},
                {"count": 1265, "group": "11001001803"},
                {"count": 1191, "group": "11001001804"},
                {"count": 1846, "group": "11001001901"},
                {"count": 1954, "group": "11001001902"},
                {"count": 1189, "group": "11001002001"},
                {"count": 1218, "group": "11001002002"},
                {"count": 1165, "group": "11001002101"},
                {"count": 1011, "group": "11001002102"},
                {"count": 1995, "group": "11001002201"},
                {"count": 1124, "group": "11001002202"},
                {"count": 1786, "group": "11001002301"},
                {"count": 1957, "group": "11001002302"},
                {"count": 1835, "group": "11001002400"},
                {"count": 867, "group": "11001002501"},
                {"count": 1818, "group": "11001002502"},
                {"count": 1728, "group": "11001002600"},
                {"count": 1661, "group": "11001002701"},
                {"count": 1622, "group": "11001002702"},
                {"count": 1398, "group": "11001002801"},
                {"count": 1557, "group": "11001002802"},
                {"count": 2337, "group": "11001002900"},
                {"count": 2247, "group": "11001003000"},
                {"count": 2531, "group": "11001003100"},
                {"count": 1222, "group": "11001003200"},
                {"count": 2899, "group": "11001003301"},
                {"count": 2173, "group": "11001003302"},
                {"count": 1859, "group": "11001003400"},
                {"count": 1703, "group": "11001003500"},
                {"count": 2163, "group": "11001003600"},
                {"count": 2206, "group": "11001003700"},
                {"count": 1831, "group": "11001003800"},
                {"count": 1989, "group": "11001003900"},
                {"count": 2258, "group": "11001004001"},
                {"count": 1980, "group": "11001004002"},
                {"count": 2448, "group": "11001004100"},
                {"count": 2244, "group": "11001004201"},
                {"count": 2077, "group": "11001004202"},
                {"count": 1926, "group": "11001004300"},
                {"count": 2827, "group": "11001004400"},
                {"count": 1856, "group": "11001004600"},
                {"count": 1689, "group": "11001004701"},
                {"count": 2466, "group": "11001004702"},
                {"count": 2173, "group": "11001004801"},
                {"count": 1796, "group": "11001004802"},
                {"count": 2093, "group": "11001004901"},
                {"count": 2196, "group": "11001004902"},
                {"count": 2447, "group": "11001005001"},
                {"count": 2175, "group": "11001005002"},
                {"count": 2379, "group": "11001005201"},
                {"count": 2060, "group": "11001005301"},
                {"count": 2703, "group": "11001005500"},
                {"count": 2178, "group": "11001005600"},
                {"count": 2676, "group": "11001005800"},
                {"count": 2691, "group": "11001005900"},
                {"count": None, "group": "11001006202"},
                {"count": 821, "group": "11001006400"},
                {"count": 2377, "group": "11001006500"},
                {"count": 1984, "group": "11001006600"},
                {"count": 2613, "group": "11001006700"},
                {"count": 1691, "group": "11001006801"},
                {"count": 2336, "group": "11001006802"},
                {"count": None, "group": "11001006804"},
                {"count": 1637, "group": "11001006900"},
                {"count": 2113, "group": "11001007000"},
                {"count": 1615, "group": "11001007100"},
                {"count": 2440, "group": "11001007200"},
                {"count": 2902, "group": "11001007301"},
                {"count": 1038, "group": "11001007304"},
                {"count": 786, "group": "11001007401"},
                {"count": 1205, "group": "11001007403"},
                {"count": 1140, "group": "11001007404"},
                {"count": 1171, "group": "11001007406"},
                {"count": 1199, "group": "11001007407"},
                {"count": 1137, "group": "11001007408"},
                {"count": 982, "group": "11001007409"},
                {"count": 1205, "group": "11001007502"},
                {"count": 1158, "group": "11001007503"},
                {"count": 931, "group": "11001007504"},
                {"count": 952, "group": "11001007601"},
                {"count": 1135, "group": "11001007603"},
                {"count": 1149, "group": "11001007604"},
                {"count": 1156, "group": "11001007605"},
                {"count": 935, "group": "11001007703"},
                {"count": 922, "group": "11001007707"},
                {"count": 991, "group": "11001007708"},
                {"count": 1055, "group": "11001007709"},
                {"count": 1146, "group": "11001007803"},
                {"count": 894, "group": "11001007804"},
                {"count": 945, "group": "11001007806"},
                {"count": 973, "group": "11001007807"},
                {"count": 768, "group": "11001007808"},
                {"count": 982, "group": "11001007809"},
                {"count": 1263, "group": "11001007901"},
                {"count": 1386, "group": "11001007903"},
                {"count": 2344, "group": "11001008001"},
                {"count": 1967, "group": "11001008002"},
                {"count": 2444, "group": "11001008100"},
                {"count": 1893, "group": "11001008200"},
                {"count": 2770, "group": "11001008301"},
                {"count": 2331, "group": "11001008302"},
                {"count": 1435, "group": "11001008402"},
                {"count": 2515, "group": "11001008410"},
                {"count": 1980, "group": "11001008701"},
                {"count": 1402, "group": "11001008702"},
                {"count": 1286, "group": "11001008802"},
                {"count": 1180, "group": "11001008803"},
                {"count": 1146, "group": "11001008804"},
                {"count": 1168, "group": "11001008903"},
                {"count": 914, "group": "11001008904"},
                {"count": 887, "group": "11001009000"},
                {"count": 1384, "group": "11001009102"},
                {"count": 1578, "group": "11001009201"},
                {"count": 1292, "group": "11001009203"},
                {"count": 1107, "group": "11001009204"},
                {"count": 1221, "group": "11001009301"},
                {"count": 1258, "group": "11001009302"},
                {"count": 1675, "group": "11001009400"},
                {"count": 1268, "group": "11001009501"},
                {"count": 2217, "group": "11001009503"},
                {"count": 1234, "group": "11001009504"},
                {"count": 1363, "group": "11001009505"},
                {"count": 1609, "group": "11001009507"},
                {"count": 1636, "group": "11001009508"},
                {"count": 1740, "group": "11001009509"},
                {"count": 859, "group": "11001009601"},
                {"count": 887, "group": "11001009602"},
                {"count": 1078, "group": "11001009603"},
                {"count": 933, "group": "11001009604"},
                {"count": 986, "group": "11001009700"},
                {"count": 1064, "group": "11001009801"},
                {"count": 1199, "group": "11001009802"},
                {"count": 1000, "group": "11001009803"},
                {"count": 1012, "group": "11001009804"},
                {"count": 933, "group": "11001009807"},
                {"count": 908, "group": "11001009810"},
                {"count": 895, "group": "11001009811"},
                {"count": 1529, "group": "11001009901"},
                {"count": 1325, "group": "11001009902"},
                {"count": 649, "group": "11001009903"},
                {"count": 876, "group": "11001009904"},
                {"count": 1036, "group": "11001009905"},
                {"count": 970, "group": "11001009906"},
                {"count": 641, "group": "11001009907"},
                {"count": 2381, "group": "11001010100"},
                {"count": 2255, "group": "11001010200"},
                {"count": 1518, "group": "11001010300"},
                {"count": 973, "group": "11001010400"},
                {"count": 1768, "group": "11001010500"},
                {"count": 2542, "group": "11001010600"},
                {"count": 2418, "group": "11001010700"},
                {"count": 1859, "group": "11001010800"},
                {"count": 1080, "group": "11001010900"},
                {"count": 1961, "group": "11001011000"},
                {"count": 1242, "group": "11001011100"},
            ]
        }

        # verify poverty_rate for census_tract
        grouping, field = "census_tract", "population_poverty"
        numerator = self.loader._get_weighted_census_results(
            grouping=grouping, field=field
        )
        denominator = self.loader._get_weighted_census_results(
            grouping=grouping, field="population"
        )
        result = self.loader._items_divide(numerator, denominator)

        for item in poverty_rate_census_tract["items"]:
            zone, value = item["group"], item["count"]
            result_value = result["items"][zone]
            self.assertEqual(
                value,
                result_value,
                "incorrect poverty_rate for census_tract: {} - "
                "expected: {}, actual: {}".format(zone, value, result_value),
            )

        # verify fraction_black for ward
        grouping, field = "ward", "population_black"
        numerator = self.loader._get_weighted_census_results(
            grouping=grouping, field=field
        )
        denominator = self.loader._get_weighted_census_results(
            grouping=grouping, field="population"
        )
        result = self.loader._items_divide(numerator, denominator)

        for item in fraction_black_ward["items"]:
            zone, value = item["group"], item["count"]
            result_value = result["items"][zone]
            result_value = float(result_value) if result_value is not None else None
            self.assertEqual(
                value,
                result_value,
                "incorrect fraction_black for ward: {} - "
                "expected: {}, actual: {}".format(zone, value, result_value),
            )

        # verify income_per_capita for neighborhood_cluster
        grouping, field = "neighborhood_cluster", "aggregate_income"
        numerator = self.loader._get_weighted_census_results(
            grouping=grouping, field=field
        )
        denominator = self.loader._get_weighted_census_results(
            grouping=grouping, field="population"
        )
        result = self.loader._items_divide(numerator, denominator)

        for item in income_per_capita_cluster["items"]:
            zone, value = item["group"], item["count"]
            result_value = float(result["items"][zone])
            self.assertEqual(
                value,
                result_value,
                "incorrect income_per_capita for "
                "neighborhood_cluster: {} - "
                "expected: {}, actual: {}".format(zone, value, result_value),
            )

        # verify upper_rent for census_tract
        grouping, field = "census_tract", "acs_upper_rent_quartile"
        result = self.loader._get_weighted_census_results(
            grouping=grouping, field=field, pop_wt_prop=True
        )

        for item in upper_rent_census_tract["items"]:
            zone, value = item["group"], item["count"]
            result_value = result["items"][zone]
            result_value = float(result_value) if result_value is not None else None
            self.assertEqual(
                value,
                result_value,
                "incorrect upper_rent for census_tract: {} - "
                "expected: {}, actual: {}".format(zone, value, result_value),
            )

        # verify median_rent for ward
        grouping, field = "ward", "acs_median_rent"
        result = self.loader._get_weighted_census_results(
            grouping=grouping, field=field, pop_wt_prop=True
        )

        for item in median_rent_ward["items"]:
            zone, value = item["group"], item["count"]
            result_value = result["items"][zone]
            result_value = float(result_value) if result_value is not None else None
            self.assertEqual(
                value,
                result_value,
                "incorrect median_rent for ward: {} - "
                "expected: {}, actual: {}".format(zone, value, result_value),
            )

        # verify lower_rent for neighborhood_cluster
        grouping, field = "neighborhood_cluster", "acs_lower_rent_quartile"
        result = self.loader._get_weighted_census_results(
            grouping=grouping, field=field, pop_wt_prop=True
        )

        for item in lower_rent_cluster["items"]:
            zone, value = item["group"], item["count"]
            result_value = result["items"][zone]
            result_value = float(result_value) if result_value is not None else None
            self.assertEqual(
                value,
                result_value,
                "incorrect lower_rent for neighborhood_cluster: "
                "{} - expected: {}, actual: {}".format(zone, value, result_value),
            )

    def test__add_census_with_weighting_fields_to_zone_facts_table(self):
        self.loader._create_zone_facts_table()
        result = self.loader._populate_zone_facts_table()
        print(result)

        self.assertEqual(True, False)

    def test__summarize_observations(self):
        building_permits_all_ward = {
            "items": [
                {"count": 1807, "group": "Ward 1"},
                {"count": 4784, "group": "Ward 2"},
                {"count": 2350, "group": "Ward 3"},
                {"count": 2364, "group": "Ward 4"},
                {"count": 3058, "group": "Ward 5"},
                {"count": 3762, "group": "Ward 6"},
                {"count": 1821, "group": "Ward 7"},
                {"count": 1238, "group": "Ward 8"},
            ]
        }

        building_permits_construction_cluster = {
            "items": [
                {"count": 168, "group": "Cluster 1"},
                {"count": 124, "group": "Cluster 10"},
                {"count": 153, "group": "Cluster 11"},
                {"count": 56, "group": "Cluster 12"},
                {"count": 166, "group": "Cluster 13"},
                {"count": 105, "group": "Cluster 14"},
                {"count": 174, "group": "Cluster 15"},
                {"count": 51, "group": "Cluster 16"},
                {"count": 168, "group": "Cluster 17"},
                {"count": 407, "group": "Cluster 18"},
                {"count": 101, "group": "Cluster 19"},
                {"count": 385, "group": "Cluster 2"},
                {"count": 151, "group": "Cluster 20"},
                {"count": 375, "group": "Cluster 21"},
                {"count": 164, "group": "Cluster 22"},
                {"count": 157, "group": "Cluster 23"},
                {"count": 76, "group": "Cluster 24"},
                {"count": 555, "group": "Cluster 25"},
                {"count": 510, "group": "Cluster 26"},
                {"count": 110, "group": "Cluster 27"},
                {"count": 62, "group": "Cluster 28"},
                {"count": 12, "group": "Cluster 29"},
                {"count": 206, "group": "Cluster 3"},
                {"count": 54, "group": "Cluster 30"},
                {"count": 115, "group": "Cluster 31"},
                {"count": 67, "group": "Cluster 32"},
                {"count": 146, "group": "Cluster 33"},
                {"count": 111, "group": "Cluster 34"},
                {"count": 39, "group": "Cluster 35"},
                {"count": 18, "group": "Cluster 36"},
                {"count": 23, "group": "Cluster 37"},
                {"count": 49, "group": "Cluster 38"},
                {"count": 138, "group": "Cluster 39"},
                {"count": 301, "group": "Cluster 4"},
                {"count": 141, "group": "Cluster 5"},
                {"count": 564, "group": "Cluster 6"},
                {"count": 215, "group": "Cluster 7"},
                {"count": 531, "group": "Cluster 8"},
                {"count": 152, "group": "Cluster 9"},
                {"count": 59, "group": "Unknown"},
            ]
        }
        result = self.loader._summarize_observations(
            "rate", "building_permits", "all", 3, "ward"
        )
        print(result)
        self.assertTrue(result)

    def test__count_observations(self):
        grouping = "census_tract"
        date_fields = {"building_permits": "issue_date", "crime": "report_date"}
        date_range_sql = (
            "({start_date}::TIMESTAMP - INTERVAL '{months} months')"
            " AND {start_date}::TIMESTAMP"
        ).format(start_date="now()", months=12)
        table_name = "building_permits"

        # test case for all census_tract building permits
        additional_wheres = " "
        result = self.loader._count_observations(
            table_name,
            grouping,
            date_field=date_fields[table_name],
            date_range_sql=date_range_sql,
            additional_wheres=additional_wheres,
        )
        self.assertIsNone(result["items"], "should return db result not None")
        self.assertEqual(result["data_id"], table_name)
        self.assertEqual(result["grouping"], grouping)
        self.assertTrue("notes" in result, "query should have failed")

        # test case for census_tract construction building permits
        grouping = "ward"
        additional_wheres = " AND permit_type_name = 'CONSTRUCTION' "
        result = self.loader._count_observations(
            table_name,
            grouping,
            date_field=date_fields[table_name],
            date_range_sql=date_range_sql,
            additional_wheres=additional_wheres,
        )
        self.assertIsNotNone(result["items"], "should return db result not " "None")
        self.assertEqual(result["data_id"], table_name)
        self.assertEqual(result["grouping"], grouping)
        self.assertTrue("notes" not in result, "query executed successfully")

        # test case for census_tract violent crime
        table_name = "crime"
        additional_wheres = (
            " AND OFFENSE IN ('ROBBERY','HOMICIDE','ASSAULT "
            "W/DANGEROUS WEAPON','SEX ABUSE')"
        )
        result = self.loader._count_observations(
            table_name,
            grouping,
            date_field=date_fields[table_name],
            date_range_sql=date_range_sql,
            additional_wheres=additional_wheres,
        )
        self.assertIsNotNone(result["items"], "should return db result not " "None")
        self.assertEqual(result["data_id"], table_name)
        self.assertEqual(result["grouping"], grouping)
        self.assertTrue("notes" not in result, "query executed successfully")

        # test case for census_tract non-violent crime
        grouping = "neighborhood_cluster"
        additional_wheres = (
            " AND OFFENSE NOT IN ('ROBBERY','HOMICIDE',"
            "'ASSAULT W/DANGEROUS WEAPON','SEX ABUSE')"
        )
        result = self.loader._count_observations(
            table_name,
            grouping,
            date_field=date_fields[table_name],
            date_range_sql=date_range_sql,
            additional_wheres=additional_wheres,
        )
        self.assertIsNotNone(result["items"], "should return db result not " "None")
        self.assertEqual(result["data_id"], table_name)
        self.assertEqual(result["grouping"], grouping)
        self.assertTrue("notes" not in result, "query executed successfully")


if __name__ == "__main__":
    unittest.main()

# census_tract construction_permits 11001007100
