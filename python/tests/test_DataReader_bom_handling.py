import sys, os
import unittest
sys.path.append(os.path.abspath('../'))

import logging

from urllib.request import urlopen

from housinginsights.ingestion import DataReader, ManifestReader
from housinginsights.ingestion import functions as ingestionfunctions


this_file = os.path.realpath(__file__)
this_dir  = os.path.dirname(this_file)
backup_suffix = '.backup'

meta_path     = os.path.abspath(this_dir + '/test_data/meta_bom_handling.json')    # TODO Update when meta.json is updated.
manifest_path = os.path.abspath(this_dir + '/test_data/manifest_bom_handling.csv') # TODO Consider updating manifest_sample

# Note: In order for unit tests to work properly, this class requires that:
#       1. any test sample data file with a leading byte order mark (BOM)
#          MUST be flagged as such in the manifest with a 'unique_data_id' that
#          includes '_bom' as a substring.
#       2. any test sample data file WITHOUT a leading byte order mark (BOM)
#          MUST be flagged as such in the manifest with a 'unique_data_id' that
#          includes '_nobom' as a substring.

meta = ingestionfunctions.load_meta_data(meta_path)
manifest = ManifestReader(manifest_path)

logging.basicConfig(level=logging.INFO)

# TODO: Update the logging message test match substrings below
#       whenever specific INFO-level (and above) message text/behavior
#       is changed in DataReader.py:
LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE = "Content (MIME) type"                             # DataReader:__init__(...)
LOG_MSG_MATCH_DEFAULT_TO_LOCAL      = "Defaulting to local data file"                   # DataReader:_download_data_file()
LOG_MSG_MATCH_ATTEMPT_TO_DOWNLOAD   = "Attempting to download file to disk"             # DataReader:_download_data_file()
LOG_MSG_MATCH_DOWNLOAD_COMPLETE     = "Download complete"                               # DataReader:_download_data_file()
LOG_MSG_MATCH_REMOTE_FILE_ACCESS    = "File will be read from remote location"          # DataReader:_set_keys()
LOG_MSG_MATCH_LEADING_BOM_FOUND     = "Leading BOM (byte order mark) found in file"     # DataReader:_set_keys()
LOG_MSG_MATCH_HEADER_FIELDS_MATCH   = "meta.json and csv field lists match completely"  # DataReader:_do_fields_match()




class BomHandlingCase(unittest.TestCase):

    # Rename any pre-existing data file(s) in preparation for testing
    # load_from='file' triggering download
    def setUp(self):
        print("Performing setUp() preparation...\n\n")
        for manifest_row in manifest:
            if manifest_row['include_flag'] == 'use':
                sample_data_folder_path = manifest_row['local_folder']
                # Adjust relative path for our location (parent directory of test_data/); strip off leading '../'
                if sample_data_folder_path[:3] == '../':
                    sample_data_folder_path = sample_data_folder_path[3:]
                    sample_data_file_path = sample_data_folder_path + '/' + manifest_row['filepath']
                else:
                    print("  Unexpected local sample data file relative path : '{}'".format(sample_data_file_path))
                    print("  Please resolve this issue.")
                    print("Exiting test...")
                    system.exit()
                if os.path.isfile(sample_data_file_path):
                    os.replace(sample_data_file_path, sample_data_file_path + backup_suffix)

    # Restore any pre-existing data file(s) renamed in setUp()
    def tearDown(self):
        print("Performing tearDown() cleanup...\n\n")
        for manifest_row in manifest:
            if manifest_row['include_flag'] == 'use':
                backup_sample_data_file_path = manifest_row['local_folder']+'/'+manifest_row['filepath']+'.backup'
                # Adjust relative file path for our location (parent directory of test_data/); strip off leading '../'
                if backup_sample_data_file_path[:3] == '../':
                    backup_sample_data_file_path = backup_sample_data_file_path[3:]
                if os.path.isfile(backup_sample_data_file_path):
                    truncate_index = len(backup_sample_data_file_path) - len(backup_suffix)
                    orig_sample_data_file_path = backup_sample_data_file_path[:truncate_index]
                    os.replace(backup_sample_data_file_path, orig_sample_data_file_path)


class TestBomHandling(BomHandlingCase):

    def test_bom_handling(self):

        print("Running test_bom_handling()...\n\n")

        for manifest_row in manifest:
            if manifest_row['include_flag'] == 'use':
                unique_data_id = manifest_row['unique_data_id']

                sample_data_folder_path = manifest_row['local_folder']
                local_sample_data_file = sample_data_folder_path + '/' + manifest_row['filepath']
                # Adjust relative path for our location (parent directory of test_data/); strip off leading '../'
                if sample_data_folder_path[:3] == '../':
                    sample_data_folder_path = sample_data_folder_path[3:]
                    local_sample_data_file = sample_data_folder_path + '/' + manifest_row['filepath']


                # Test Case 1: Test sample data file with bom in header row
                if "_bom" in unique_data_id:

                    print("  Test Case 1: Test sample data file with bom in header row...\n\n")

                    self.assertIn("_bom", unique_data_id)

                    # Subtest Case 1a: File with bom in header row:
                    #                  load_from='file': Sample data file does not already exist
                    #                  locally and DataReader downloads remote file
                    with self.subTest(subtest='1a'):
                        subtest1a_success = self._test_bom_handling_case_1a(manifest_row,
                                                                            local_sample_data_file)
                        self.assertTrue(subtest1a_success, "If failed, test case 1a failed.\n")

                    # Subtest Case 1b: File with bom in header row:
                    #                  load_from='file': Sample data file already exists locally and
                    #                  DataReader reads from local file
                    with self.subTest(subtest='1b'):
                        subtest1b_success = self._test_bom_handling_case_1b(manifest_row,
                                                                            local_sample_data_file)
                        self.assertTrue(subtest1b_success, "If failed, test case 1b failed.\n")

                    # Subtest Case 1c: File with bom in header row:
                    #                  load_from='s3': DataReader reads from remote file
                    with self.subTest(subtest='1c'):
                        subtest1c_success = self._test_bom_handling_case_1c(manifest_row,
                                                                            local_sample_data_file)
                        self.assertTrue(subtest1c_success, "If failed, test case 1c failed.\n")


                # Test Case 2: Test sample data file without bom in header row
                else:

                    print("  Test Case 2: Test sample data file without bom in header row...\n\n")

                    self.assertIn("_nobom", unique_data_id)

                    # Subtest Case 2a: File without bom in header row:
                    #                  load_from='file': Sample data file does not already exist
                    #                  locally and DataReader downloads remote file
                    with self.subTest(subtest='2a'):
                        subtest2a_success = self._test_bom_handling_case_2a(manifest_row,
                                                                            local_sample_data_file)
                        self.assertTrue(subtest2a_success, "If failed, test case 2a failed.\n")

                    # Subtest Case 2b: File without bom in header row:
                    #                  load_from='file': Sample data file already exists locally and
                    #                  DataReader reads from local file
                    with self.subTest(subtest='2b'):
                        subtest2b_success = self._test_bom_handling_case_2b(manifest_row,
                                                                            local_sample_data_file)
                        self.assertTrue(subtest2b_success, "If failed, test case 2b failed.\n")

                    # Subtest Case 2c: File without bom in header row:
                    #                  load_from='s3': DataReader reads from remote file
                    with self.subTest(subtest='2c'):
                        subtest2c_success = self._test_bom_handling_case_2c(manifest_row,
                                                                            local_sample_data_file)
                        self.assertTrue(subtest2c_success, "If failed, test case 2c failed.\n")



    # Subtest Case 1a: File with bom in header row:
    #                  load_from='file': Sample data file does not already exist locally
    #                  and DataReader downloads remote file
    def _test_bom_handling_case_1a(self, manifest_row, local_sample_data_file):

        print("    Subtest Case 1a: Test sample data file with bom in header row:")
        print("                     load_from='file': Sample data file does not already \n" \
              "                     exist locally and DataReader downloads remote file\n")

        print("      Test File: '{}'\n".format(local_sample_data_file))

        unique_data_id = manifest_row['unique_data_id']

        case_name = "DataReader instantiation for input '{}' with BOM header, " \
                    "triggered remote download case.".format(unique_data_id)

        self.assertFalse(os.path.isfile(local_sample_data_file),
                         "If failed, input file '{}' unexpectedly exists already. ({})".format(
                            os.path.basename(local_sample_data_file), case_name))

        with self.assertLogs(level='INFO') as logged:
            csv_reader = DataReader(meta=meta, manifest_row=manifest_row, load_from='file')
        self.assertIsInstance(csv_reader, DataReader,
                              "If failed, DataReader was not instantiated. ({})".format(case_name))
        self.assertGreater(len(logged.output), 0,
                           "If failed, no output was logged as expected. ({})".format(case_name))
        if len(logged.output) == 4:
            self.assertIn(LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, logged.output[0],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, case_name))
            self.assertIn(LOG_MSG_MATCH_ATTEMPT_TO_DOWNLOAD  , logged.output[1],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_ATTEMPT_TO_DOWNLOAD  , case_name))
            self.assertIn(LOG_MSG_MATCH_DOWNLOAD_COMPLETE    , logged.output[2],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_DOWNLOAD_COMPLETE  , case_name))
            self.assertIn(LOG_MSG_MATCH_LEADING_BOM_FOUND    , logged.output[3],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_LEADING_BOM_FOUND  , case_name))
        else: # Force test failure:
            self.assertEqual(len(logged.output), 4,
                             "If failed, there was a different number of output lines than expected. " \
                             "({})".format(case_name))

        with self.assertLogs(level='INFO') as logged:
            fields_match_success = csv_reader._do_fields_match()
        self.assertTrue(fields_match_success,
                        "If failed, sample meta.json and data file header field names did not match. " \
                        "({})".format(case_name))
        self.assertIn(LOG_MSG_MATCH_HEADER_FIELDS_MATCH, logged.output[0],
                      "If failed, sample meta.json and data file header field names did not match. " \
                      "({})\n" \
                      "If failed, double-check that 'source_name' values in '{}' fully match " \
                      "csv header field names in '{}'.".format(
                        case_name, os.path.basename(meta_path),
                                   os.path.basename(local_sample_data_file)))

        with open(local_sample_data_file, mode='r', encoding=manifest_row['encoding']) as f:
            # Get array of data row lines from source sample data file to compare against DataReader data row:
            data_lines_file = f.read().replace('"', '').replace("\r\n", "\n").split('\n')[1:]
        for i,d in enumerate(csv_reader):
            # Convert DataReader data row dicts into csv strings and compare to file data row lines:
            data_row_csv = ','.join(d[k] for k in csv_reader.keys)
            self.assertEqual(data_lines_file[i], data_row_csv)
        with open(local_sample_data_file, mode='rb') as f:
            # Verify that source sample data file has BOM:
            self.assertEqual(f.read(3).hex(), "efbbbf")

        print("    Subtest Case 1a: Tests completed successfully.\n\n")
        return True


    # Subtest Case 1b: File with bom in header row:
    #                  load_from='file': Sample data file already exists locally
    #                  and DataReader reads from local file
    def _test_bom_handling_case_1b(self, manifest_row, local_sample_data_file):

        print("    Subtest Case 1b: Test sample data file with bom in header row:")
        print("                     load_from='file': Sample data file already exists locally \n" \
              "                     and DataReader reads from local file\n")

        print("      Test File: '{}'\n".format(local_sample_data_file))

        unique_data_id = manifest_row['unique_data_id']

        case_name = "DataReader instantiation for input '{}' with BOM header, " \
                    "local file case.".format(unique_data_id)

        self.assertTrue(os.path.isfile(local_sample_data_file),
                        "If failed, input file '{}' not found locally as expected. ({})".format(
                            os.path.basename(local_sample_data_file), case_name))

        with self.assertLogs(level='INFO') as logged:
            csv_reader = DataReader(meta=meta, manifest_row=manifest_row, load_from='file')
        self.assertIsInstance(csv_reader, DataReader,
                              "If failed, DataReader was not instantiated. ({})".format(case_name))
        self.assertGreater(len(logged.output), 0,
                           "If failed, no output was logged as expected. ({})".format(case_name))
        if len(logged.output) == 3:
            self.assertIn(LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, logged.output[0],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, case_name))
            self.assertIn(LOG_MSG_MATCH_DEFAULT_TO_LOCAL     , logged.output[1],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_DEFAULT_TO_LOCAL     , case_name))
            self.assertIn(LOG_MSG_MATCH_LEADING_BOM_FOUND    , logged.output[2],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_LEADING_BOM_FOUND    , case_name))
        else: # Force test failure:
            self.assertEqual(len(logged.output), 3,
                             "If failed, there was a different number of output lines than expected. " \
                             "({})".format(case_name))

        with self.assertLogs(level='INFO') as logged:
            fields_match_success = csv_reader._do_fields_match()
        self.assertTrue(fields_match_success,
                        "If failed, sample meta.json and data file header field names did not match. " \
                        "({})".format(case_name))
        self.assertIn(LOG_MSG_MATCH_HEADER_FIELDS_MATCH, logged.output[0],
                      "If failed, sample meta.json and data file header field names did not match. " \
                      "({})\n" \
                      "If failed, double-check that 'source_name' values in '{}' fully match " \
                      "csv header field names in '{}'.".format(
                        case_name, os.path.basename(meta_path),
                                   os.path.basename(local_sample_data_file)))

        with open(local_sample_data_file, mode='r', encoding=manifest_row['encoding']) as f:
            # Get array of data row lines from source sample data file to compare against DataReader data row:
            data_lines_file = f.read().replace('"', '').replace("\r\n", "\n").split('\n')[1:]
        for i,d in enumerate(csv_reader):
            # Convert DataReader data row dicts into csv strings and compare to file data row lines:
            data_row_csv = ','.join(d[k] for k in csv_reader.keys)
            self.assertEqual(data_lines_file[i], data_row_csv)
        with open(local_sample_data_file, mode='rb') as f:
            # Verify that source sample data file has BOM:
            self.assertEqual(f.read(3).hex(), "efbbbf")

        print("    Subtest Case 1b: Tests completed successfully.\n\n")
        return True


    # Subtest Case 1c: File with bom in header row:
    #                  load_from='s3': DataReader reads from remote file
    def _test_bom_handling_case_1c(self, manifest_row, local_sample_data_file):

        print("    Subtest Case 1c: Test sample data file with bom in header row:")
        print("                     load_from='s3': DataReader reads from remote file\n")

        print("      Test File: '{}'\n".format(local_sample_data_file))

        unique_data_id = manifest_row['unique_data_id']

        case_name = "DataReader instantiation for input '{}' with BOM header, " \
                    "read from remote file case.".format(unique_data_id)

        with self.assertLogs(level='INFO') as logged:
            csv_reader = DataReader(meta=meta, manifest_row=manifest_row, load_from='s3')
        self.assertIsInstance(csv_reader, DataReader,
                              "If failed, DataReader was not instantiated. ({})".format(case_name))
        self.assertGreater(len(logged.output), 0,
                           "If failed, no output was logged as expected. ({})".format(case_name))
        if len(logged.output) == 3:
            self.assertIn(LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, logged.output[0],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, case_name))
            self.assertIn(LOG_MSG_MATCH_REMOTE_FILE_ACCESS   , logged.output[1],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_REMOTE_FILE_ACCESS   , case_name))
            self.assertIn(LOG_MSG_MATCH_LEADING_BOM_FOUND    , logged.output[2],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_LEADING_BOM_FOUND    , case_name))
        else: # Force test failure:
            self.assertEqual(len(logged.output), 3,
                             "If failed, there was a different number of output lines than expected. " \
                             "({})".format(case_name))

        with self.assertLogs(level='INFO') as logged:
            fields_match_success = csv_reader._do_fields_match()
        self.assertTrue(fields_match_success,
                        "If failed, sample meta.json and data file header field names did not match. " \
                        "({})".format(case_name))
        self.assertIn(LOG_MSG_MATCH_HEADER_FIELDS_MATCH, logged.output[0],
                      "If failed, sample meta.json and data file header field names did not match. " \
                      "({})\n" \
                      "If failed, double-check that 'source_name' values in '{}' fully match " \
                      "csv header field names in '{}'.".format(
                        case_name, os.path.basename(meta_path),
                                   os.path.basename(local_sample_data_file)))

        s3_path = os.path.join( manifest_row['s3_folder'],
                                manifest_row['filepath'].strip("\/") ).replace("\\","/")
        with urlopen(s3_path) as ftpstream:
            # Verify that source sample data file has BOM:
            header_line_file = ftpstream.readline().decode('latin-1')
            self.assertEqual(header_line_file[:3], "ï»¿")
            for i,d in enumerate(csv_reader):
                data_line_file = ftpstream.readline().decode(manifest_row['encoding']).replace('"', '').replace("\n", '')
                if data_line_file == b'':
                    break
                # Convert DataReader data row dicts into csv string and compare to file data row line:
                data_row_csv = ','.join(d[k] for k in csv_reader.keys)
                self.assertEqual(data_line_file, data_row_csv)

        print("    Subtest Case 1c: Tests completed successfully.\n\n")
        return True


    # Subtest Case 2a: File without bom in header row:
    #                  load_from='file': Sample data file does not already exist locally
    #                  and DataReader downloads remote file
    def _test_bom_handling_case_2a(self, manifest_row, local_sample_data_file):

        print("    Subtest Case 2a: Test sample data file without bom in header row:")
        print("                     load_from='file': Sample data file does not already exist locally \n" \
              "                     and DataReader downloads remote file\n")

        print("      Test File: '{}'\n".format(local_sample_data_file))

        unique_data_id = manifest_row['unique_data_id']

        case_name = "DataReader instantiation for input '{}' without BOM header, " \
                    "triggered remote download case.".format(unique_data_id)

        self.assertFalse(os.path.isfile(local_sample_data_file),
                         "If failed, input file '{}' unexpectedly exists already. ({})".format(
                            os.path.basename(local_sample_data_file), case_name))

        with self.assertLogs(level='INFO') as logged:
            csv_reader = DataReader(meta=meta, manifest_row=manifest_row, load_from='file')
        self.assertIsInstance(csv_reader, DataReader,
                              "If failed, DataReader was not instantiated. ({})".format(case_name))

        self.assertGreater(len(logged.output), 0,
                           "If failed, no output was logged as expected. ({})".format(case_name))
        if len(logged.output) == 3:
            self.assertNotIn(LOG_MSG_MATCH_LEADING_BOM_FOUND  , logged.output[0],
                             "If failed, unexpected '{}' found in logged output. ({})".format(
                                LOG_MSG_MATCH_LEADING_BOM_FOUND, case_name))
            self.assertNotIn(LOG_MSG_MATCH_LEADING_BOM_FOUND  , logged.output[1],
                             "If failed, unexpected '{}' found in logged output. ({})".format(
                                LOG_MSG_MATCH_LEADING_BOM_FOUND, case_name))
            self.assertNotIn(LOG_MSG_MATCH_LEADING_BOM_FOUND  , logged.output[2],
                             "If failed, unexpected '{}' found in logged output. ({})".format(
                                LOG_MSG_MATCH_LEADING_BOM_FOUND, case_name))

            self.assertIn(LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, logged.output[0],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, case_name))
            self.assertIn(LOG_MSG_MATCH_ATTEMPT_TO_DOWNLOAD  , logged.output[1],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_ATTEMPT_TO_DOWNLOAD  , case_name))
            self.assertIn(LOG_MSG_MATCH_DOWNLOAD_COMPLETE    , logged.output[2],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_DOWNLOAD_COMPLETE    , case_name))
        else: # Force test failure:
            self.assertEqual(len(logged.output), 3,
                             "If failed, there was a different number of output lines than expected. " \
                             "({})".format(case_name))

        with self.assertLogs(level='INFO') as logged:
            fields_match_success = csv_reader._do_fields_match()
        self.assertTrue(fields_match_success,
                        "If failed, sample meta.json and data file header field names did not match. " \
                        "({})".format(case_name))
        self.assertIn(LOG_MSG_MATCH_HEADER_FIELDS_MATCH, logged.output[0],
                      "If failed, sample meta.json and data file header field names did not match. " \
                      "({})\n" \
                      "If failed, double-check that 'source_name' values in '{}' fully match " \
                      "csv header field names in '{}'.".format(
                        case_name, os.path.basename(meta_path),
                                   os.path.basename(local_sample_data_file)))

        with open(local_sample_data_file, mode='r', encoding=manifest_row['encoding']) as f:
            # Get data row lines from source sample data file to compare against DataReader data row:
            data_lines_file = f.read().replace('"', '').replace("\r\n", "\n").split('\n')[1:]
        for i,d in enumerate(csv_reader):
            # Convert DataReader data row dicts into csv strings and compare to file data row lines:
            data_row_csv = ','.join(d[k] for k in csv_reader.keys)
            self.assertEqual(data_lines_file[i], data_row_csv)

        print("    Subtest Case 2a: Tests completed successfully.\n\n")
        return True


    # Subtest Case 2b: File without bom in header row:
    #                  load_from='file': Sample data file already exists locally
    #                  and DataReader reads from local file
    def _test_bom_handling_case_2b(self, manifest_row, local_sample_data_file):

        print("    Subtest Case 2b: Test sample data file without bom in header row:")
        print("                     load_from='file': Sample data file already exists locally \n" \
              "                     and DataReader reads from local file\n")

        print("      Test File: '{}'\n".format(local_sample_data_file))

        unique_data_id = manifest_row['unique_data_id']

        case_name = "DataReader instantiation for input '{}' without BOM header, " \
                    "local file case.".format(unique_data_id)

        self.assertTrue(os.path.isfile(local_sample_data_file),
                        "If failed, input file '{}' not found locally as expected. ({})".format(
                            os.path.basename(local_sample_data_file), case_name))

        with self.assertLogs(level='INFO') as logged:
            csv_reader = DataReader(meta=meta, manifest_row=manifest_row, load_from='file')
        self.assertIsInstance(csv_reader, DataReader,
                              "If failed, DataReader was not instantiated. ({})".format(case_name))
        self.assertGreater(len(logged.output), 0,
                           "If failed, no output was logged as expected. ({})".format(case_name))
        if len(logged.output) == 2:
            self.assertNotIn(LOG_MSG_MATCH_LEADING_BOM_FOUND, logged.output[0],
                             "If failed, unexpected '{}' found in logged output. ({})".format(
                                LOG_MSG_MATCH_LEADING_BOM_FOUND, case_name))
            self.assertNotIn(LOG_MSG_MATCH_LEADING_BOM_FOUND, logged.output[1],
                             "If failed, unexpected '{}' found in logged output. ({})".format(
                                LOG_MSG_MATCH_LEADING_BOM_FOUND, case_name))

            self.assertIn(LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, logged.output[0],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, case_name))
            self.assertIn(LOG_MSG_MATCH_DEFAULT_TO_LOCAL     , logged.output[1],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_DEFAULT_TO_LOCAL     , case_name))
        else: # Force test failure:
            self.assertGreater(len(logged.output), 2,
                               "If failed, there were more output lines logged than expected. " \
                               "({})".format(case_name))

        with self.assertLogs(level='INFO') as logged:
            fields_match_success = csv_reader._do_fields_match()
        self.assertTrue(fields_match_success,
                        "If failed, sample meta.json and data file header field names did not match. " \
                        "({})".format(case_name))
        self.assertIn(LOG_MSG_MATCH_HEADER_FIELDS_MATCH, logged.output[0],
                      "If failed, sample meta.json and data file header field names did not match. " \
                      "({})\n" \
                      "If failed, double-check that 'source_name' values in '{}' fully match " \
                      "csv header field names in '{}'.".format(
                        case_name, os.path.basename(meta_path),
                                   os.path.basename(local_sample_data_file)))

        with open(local_sample_data_file, mode='r', encoding=manifest_row['encoding']) as f:
            # Get array of data row lines from source sample data file to compare against DataReader data row:
            data_lines_file = f.read().replace('"', '').replace("\r\n", "\n").split('\n')[1:]
        for i,d in enumerate(csv_reader):
            # Convert DataReader data row dicts into csv strings and compare to file data row lines:
            data_row_csv = ','.join(d[k] for k in csv_reader.keys)
            self.assertEqual(data_lines_file[i], data_row_csv)

        print("    Subtest Case 2b: Tests completed successfully.\n\n")
        return True


    # Subtest Case 2c: File without bom in header row:
    #                  load_from='s3': DataReader reads from remote file
    def _test_bom_handling_case_2c(self, manifest_row, local_sample_data_file):

        print("    Subtest Case 2c: Test sample data file without bom in header row:")
        print("                     load_from='s3': DataReader reads from remote file\n")

        print("      Test File: '{}'\n".format(local_sample_data_file))

        unique_data_id = manifest_row['unique_data_id']

        case_name = "DataReader instantiation for input '{}' without BOM header, " \
                    "read from remote file case.".format(unique_data_id)

        with self.assertLogs(level='INFO') as logged:
            csv_reader = DataReader(meta=meta, manifest_row=manifest_row, load_from='s3')
        self.assertIsInstance(csv_reader, DataReader,
                              "If failed, DataReader was not instantiated. ({})".format(case_name))
        self.assertGreater(len(logged.output), 0,
                           "If failed, no output was logged as expected. ({})".format(case_name))
        if len(logged.output) == 2:
            self.assertNotIn(LOG_MSG_MATCH_LEADING_BOM_FOUND , logged.output[0],
                             "If failed, unexpected '{}' found in logged output. ({})".format(
                                LOG_MSG_MATCH_LEADING_BOM_FOUND, case_name))
            self.assertNotIn(LOG_MSG_MATCH_LEADING_BOM_FOUND , logged.output[1],
                             "If failed, unexpected '{}' found in logged output. ({})".format(
                                LOG_MSG_MATCH_LEADING_BOM_FOUND, case_name))

            self.assertIn(LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, logged.output[0],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_HTTP_HDR_CONTENT_TYPE, case_name))
            self.assertIn(LOG_MSG_MATCH_REMOTE_FILE_ACCESS   , logged.output[1],
                          "If failed, missing expected '{}' in logged output. ({})".format(
                            LOG_MSG_MATCH_REMOTE_FILE_ACCESS   , case_name))
        else: # Force test failure:
            self.assertEqual(len(logged.output), 2,
                             "If failed, there was a different number of output lines than expected. " \
                             "({})".format(case_name))

        with self.assertLogs(level='INFO') as logged:
            fields_match_success = csv_reader._do_fields_match()
        self.assertTrue(fields_match_success,
                        "If failed, sample meta.json and data file header field names did not match. " \
                        "({})".format(case_name))
        self.assertIn(LOG_MSG_MATCH_HEADER_FIELDS_MATCH, logged.output[0],
                      "If failed, sample meta.json and data file header field names did not match. " \
                      "({})\n" \
                      "If failed, double-check that 'source_name' values in '{}' fully match " \
                      "csv header field names in '{}'.".format(
                        case_name, os.path.basename(meta_path),
                                   os.path.basename(local_sample_data_file)))

        s3_path = os.path.join(manifest_row['s3_folder'], manifest_row['filepath'].strip("\/")).replace("\\","/")
        with urlopen(s3_path) as ftpstream:
            ftpstream.readline()    # Ignore header row of remote sample source data file
            for i,d in enumerate(csv_reader):
                data_line_file = ftpstream.readline().decode(manifest_row['encoding']).replace('"', '').replace('\r', '').replace('\n', '')
                if data_line_file == b'':
                    break
                # Convert DataReader data row dicts into csv string and compare to remote file data row line:
                data_row_csv = ','.join(d[k] for k in csv_reader.keys)
                self.assertEqual(data_line_file, data_row_csv)

        print("    Subtest Case 2c: Tests completed successfully.\n\n")
        return True



if __name__ == '__main__':
    unittest.main()
