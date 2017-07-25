"""
Module provides the api connection class for pulling DHCD DFD data
on projects pending funding and development
from https://octo.quickbase.com/db/<DB_ID>
Quickbase API
"""


import sys, os
import string

# Enable relative package imports when running this file as a script (i.e. for testing purposes).
python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir, os.pardir))
sys.path.append(python_filepath)


from collections import OrderedDict

from xml.etree.ElementTree import Element, ElementTree
from xml.etree.ElementTree import fromstring as xml_fromstring

from xmljson import parker as xml_to_json

import json


from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.dhcd import APP_ID, TABLE_ID_MAPPING, \
                                                        APP_METADATA_FIELDS, \
                                                        TABLE_METADATA_FIELDS, \
                                                        DhcdResult
INCLUDE_ALL_FIELDS = True


class DhcdApiConn(BaseApiConn):
    """
    API Interface to the DHCD DFD data on projects
    pending funding and development.

    Inherits from BaseApiConn class.
    """

    BASEURL                    = 'https://octo.quickbase.com/db'

    PARAMS_METADATA            = {'a': 'API_GetSchema'}

    PARAMS_DATA_ALL_FIELDS     = {'a': 'API_DoQuery', 'query': '{\'1\'.XEX.\'0\'}', 'clist': 'a', 'slist': '3'}

    PARAMS_DATA_DEFAULT_FIELDS = {'a': 'API_DoQuery', 'query': '{\'1\'.XEX.\'0\'}'}


    def __init__(self):

        super().__init__(DhcdApiConn.BASEURL)

        # unique_data_id format: 'dhcd_dfd_' + <lowercase_table_name>
        self._available_unique_data_ids = [ 'dhcd_dfd_projects', 'dhcd_dfd_properties' #,
#                                            'dhcd_dfd_units', 'dhcd_dfd_loans', 'dhcd_dfd_modifications',
#                                            'dhcd_dfd_lihtc_allocations', 'dhcd_dfd_construction_activity',
#                                            'dhcd_dfd_funding_sources', 'dhcd_dfd_8609s', 'dhcd_dfd_8610s',
#                                            'dhcd_dfd_source_use', 'dhcd_dfd_ami_levels', 'dhcd_dfd_fiscal_years',
#                                            'dhcd_dfd_organizations', 'dhcd_dfd_teams', 'dhcd_dfd_project_managers',
#                                            'dhcd_dfd_funding_increases', 'dhcd_dfd_lihtc_fees',
#                                            'dhcd_dfd_lihtc___bins', 'dhcd_dfd_council_packages',
#                                            'dhcd_dfd_policies_and_procedures', 'dhcd_dfd_dhcd_documents',
#                                            'dhcd_dfd_images_icons'
                                          ]
        self._app_dbid = APP_ID
        self._table_names = {
                                'dhcd_dfd_projects':                'Projects',
                                'dhcd_dfd_properties':              'Properties' #,
#                                'dhcd_dfd_units':                   'Units',
#                                'dhcd_dfd_loans':                   'Loans',
#                                'dhcd_dfd_modifications':           'Modifications',
#                                'dhcd_dfd_lihtc_allocations':       'LIHTC Allocations',
#                                'dhcd_dfd_construction_activity':   'Construction Activity',
#                                'dhcd_dfd_funding_sources':         'Funding Sources',
#                                'dhcd_dfd_8609s':                   '8609s',
#                                'dhcd_dfd_8610s':                   '8610s',
#                                'dhcd_dfd_source_use':              'Source/Use',
#                                'dhcd_dfd_ami_levels':              'AMI Levels',
#                                'dhcd_dfd_fiscal_years':            'Fiscal Years',
#                                'dhcd_dfd_organizations':           'Organizations',
#                                'dhcd_dfd_teams':                   'Teams'
#                                'dhcd_dfd_project_managers':        'Project Managers',
#                                'dhcd_dfd_funding_increases':       'Funding Increases',
#                                'dhcd_dfd_lihtc_fees':              'LIHTC Fees',
#                                'dhcd_dfd_lihtc___bins':            'LIHTC - BINs',
#                                'dhcd_dfd_council_packages':        'Council Packages',
#                                'dhcd_dfd_policies_and_procedures': 'Policies and Procedures',
#                                'dhcd_dfd_dhcd_documents':          'DHCD Documents',
#                                'dhcd_dfd_images_icons':            'Images/Icons'
                            }
        self._urls = { unique_data_id: '/' + TABLE_ID_MAPPING[self._table_names[unique_data_id]] \
                        for unique_data_id in self._available_unique_data_ids }

        identifier_unallowed_chars = string.punctuation + string.whitespace
        replacement_underscores = ''.join('_' * len(identifier_unallowed_chars))
        self._identifier_translation_map = str.maketrans(identifier_unallowed_chars, replacement_underscores)

        self._fields = {}
        self._params = {}

        if INCLUDE_ALL_FIELDS:
            self._get_metadata()
        else:
            self._get_metadata(default_display_only=True)


    def _get_metadata(self, default_display_only=False):
        """
        Retrieves metadata about the DHCD DFD Quick Base app and its member tables
        (including field metadata and relationships) and saves this in two CSV files.

        Also, for each unique data id corresponding to a table, (1) builds a field
        reference list of all relevant fields, and (2) sets the query parameter string
        (including the sort field parameter) used when saving table data in get_data(...).

        :param default_display_only: Indicates whether or not to only include default
                                     display fields in the field reference list;
                                     default is False (gets all available table fields).
        :type  default_display_only: Boolean.
        """
        output_path_dir = os.path.dirname(self.output_paths[self._available_unique_data_ids[0]])
        output_path_app_metadata = os.path.join(output_path_dir, '_dhcd_dfd_app_metadata.csv')
        output_path_table_metadata = os.path.join(output_path_dir, '_dhcd_dfd_table_metadata.csv')

        app_metadata_result = self.get('/' + self._app_dbid, params=DhcdApiConn.PARAMS_METADATA)
        app_tables_metadata_xml = xml_fromstring(app_metadata_result.text).findall('./table/chdbids/chdbid')

        app_metadata = OrderedDict()
        table_metadata = OrderedDict()
        field_count = 0
        for app_table_metadata in app_tables_metadata_xml:

            table_dbid = app_table_metadata.text

            table_metadata_result = self.get('/' + table_dbid, params=DhcdApiConn.PARAMS_METADATA)
            # Strip out singly-occurring line break tags to prevent truncation of multi-line formulas
            table_metadata_full = table_metadata_result.text.replace("<BR/>\n<BR/>", "<br />\n<br />")
            table_metadata_full = table_metadata_result.text.replace("<BR/>", "")
            table_metadata_xml_root = xml_fromstring(table_metadata_full)
            errcode = int(table_metadata_xml_root.find('./errcode').text)
            if errcode == 0:
                table_metadata_xml_orig = table_metadata_xml_root.find('./table/original')
                table_name = table_metadata_xml_root.find('./table/name').text
                table_name_snake_case = table_name.lower().translate(self._identifier_translation_map)
                unique_data_id = None
                if 'dhcd_dfd_'+table_name_snake_case in self._available_unique_data_ids:
                    unique_data_id = 'dhcd_dfd_' + table_name_snake_case
                    self._fields[unique_data_id] = []

                table_metadata_xml_fields = table_metadata_xml_root.findall('./table/fields/field')
                table_metadata[table_dbid] = OrderedDict()
                field_line_start = field_count + 2

                for field_xml in table_metadata_xml_fields:

                    fid = int(field_xml.get('id'))
                    table_metadata[table_dbid][fid] = OrderedDict()

                    field_label = field_xml.find('label').text
                    field_name = field_label.lower().translate(self._identifier_translation_map)

                    # For any fields that belong to composite fields (e.g. address component fields),
                    # resolve the full field name by prepending the parent field name
                    parent_fid = None
                    if field_xml.find('parentFieldID') is not None:
                        parent_fid = int(field_xml.find('parentFieldID').text)
                        if parent_fid in table_metadata[table_dbid]:
                            parent_field_name = table_metadata[table_dbid][parent_fid]['field_name']
                        else:
                            parent_field_label = table_metadata_xml_root.find("./table/fields/field[@id='{}']/label".format(str(parent_fid))).text
                            parent_field_name = parent_field_label.lower().translate(self._identifier_translation_map)
                        if parent_field_name[0].isdigit():
                            parent_field_name = '_' + parent_field_name
                        field_name = '__'.join([parent_field_name, field_name])

                    if field_name[0].isdigit():
                        field_name = '_' + field_name

                    # For any composite fields (e.g. address fields), get child/component fields
                    child_fids = []
                    for child_field in field_xml.findall('./compositeFields/compositeField'):
                        child_fids.append(child_field.get('id'))
                    child_fids = '|'.join(child_fids) if len(child_fids) > 0 else None

                    table_metadata[table_dbid][fid]['table_name'] = table_name
                    table_metadata[table_dbid][fid]['field_name'] = field_name
                    table_metadata[table_dbid][fid]['field_label'] = field_label
                    table_metadata[table_dbid][fid]['field_id'] = str(fid)
                    table_metadata[table_dbid][fid]['field_type'] = field_xml.get('field_type')
                    table_metadata[table_dbid][fid]['base_type'] = field_xml.get('base_type')
                    table_metadata[table_dbid][fid]['appears_by_default'] = field_xml.find('appears_by_default').text

                    table_metadata[table_dbid][fid]['composite_field_parent_fid'] = parent_fid
                    table_metadata[table_dbid][fid]['composite_field_child_fids'] = child_fids

                    table_metadata[table_dbid][fid]['mode'] = field_xml.get('mode')

                    table_metadata[table_dbid][fid]['formula'] = None
                    if field_xml.find('formula') is not None:
                        table_metadata[table_dbid][fid]['formula'] = field_xml.find('formula').text

                    table_metadata[table_dbid][fid]['choices'] = None
                    if field_xml.find('choices') is not None:
                        table_metadata[table_dbid][fid]['choices'] = ""
                        for choice in field_xml.findall('./choices/choice'):
                            table_metadata[table_dbid][fid]['choices'] += "\n" + choice.text \
                                                    if len(table_metadata[table_dbid][fid]['choices']) > 0 \
                                                    else choice.text

                    table_metadata[table_dbid][fid]['lookup_target_fid'] = None
                    table_metadata[table_dbid][fid]['lookup_source_fid'] = None
                    if table_metadata[table_dbid][fid]['mode'] == 'lookup':
                        if field_xml.find('lutfid') is not None:
                            table_metadata[table_dbid][fid]['lookup_target_fid'] = field_xml.find('lutfid').text
                        if field_xml.find('lusfid') is not None:
                            table_metadata[table_dbid][fid]['lookup_source_fid'] = field_xml.find('lusfid').text

                    table_metadata[table_dbid][fid]['dblink_target_dbid'] = None
                    table_metadata[table_dbid][fid]['dblink_target_fid'] = None
                    table_metadata[table_dbid][fid]['dblink_source_fid'] = None
                    if table_metadata[table_dbid][fid]['mode'] == 'virtual' and \
                        table_metadata[table_dbid][fid]['field_type'] == 'dblink':
                        if field_xml.find('target_dbid') is not None:
                            table_metadata[table_dbid][fid]['dblink_target_dbid'] = field_xml.find('target_dbid').text
                        if field_xml.find('target_fid') is not None:
                            table_metadata[table_dbid][fid]['dblink_target_fid'] = field_xml.find('target_fid').text
                        if field_xml.find('source_fid') is not None:
                            table_metadata[table_dbid][fid]['dblink_source_fid'] = field_xml.find('source_fid').text
                    table_metadata[table_dbid][fid]['fkey_table_app_dbid'] = None
                    table_metadata[table_dbid][fid]['fkey_table_alias'] = None
                    if field_xml.find('mastag') is not None:
                        fkey_ref = field_xml.find('mastag').text.split('.')
                        if len(fkey_ref) == 2:
                            table_metadata[table_dbid][fid]['fkey_table_app_dbid'] = fkey_ref[0]
                            table_metadata[table_dbid][fid]['fkey_table_alias'] = fkey_ref[1].lower()
                        else:
                            table_metadata[table_dbid][fid]['fkey_table_app_dbid'] = None
                            table_metadata[table_dbid][fid]['fkey_table_alias'] = fkey_ref[0].lower()

                    table_metadata[table_dbid][fid]['field_help'] = field_xml.find('fieldhelp').text

                    # For each unique data id corresponding to a table,
                    # build a list of all relevant fields
                    if unique_data_id is not None and \
                        (not default_display_only or \
                         table_metadata[table_dbid][fid]['appears_by_default'] == '1'):
                        self._fields[unique_data_id].append(field_name)

                    field_count += 1

                field_line_end = field_count + 1

                app_metadata[table_dbid] = OrderedDict([
					  ('table_name',                table_name),
                      ('table_dbid',                table_dbid),
                      ('table_alias',               app_table_metadata.get('name')),
                      ('key_fid',                   table_metadata_xml_orig.find('key_fid').text),
                      ('default_sort_fid',          table_metadata_xml_orig.find('def_sort_fid').text),
                      ('default_sort_order',        table_metadata_xml_orig.find('def_sort_order').text),
                      ('single_record_name',        table_metadata_xml_orig.find('single_record_name').text),
                      ('plural_record_name',        table_metadata_xml_orig.find('plural_record_name').text),
                      ('field_metadata_line_start', field_line_start),
                      ('field_metadata_line_end',   field_line_end)
                    ])

                if unique_data_id is not None and unique_data_id in self._fields:
                    # While not strictly a field, Quick Base always includes final 'update_id':
                    self._fields[unique_data_id].append('update_id')
                    # Set the query parameter string (including the sort field parameter):
                    if not default_display_only:
                        self._params[unique_data_id] = DhcdApiConn.PARAMS_DATA_ALL_FIELDS
                    else:
                        self._params[unique_data_id] = DhcdApiConn.PARAMS_DATA_DEFAULT_FIELDS
                    self._params[unique_data_id]['slist'] = app_metadata[table_dbid]['default_sort_fid']

        all_tables_field_metadata = [ list(field_metadata_row.values()) \
                                        for all_field_metadata in table_metadata.values() \
                                        for field_metadata_row in all_field_metadata.values() ]
        self.result_to_csv(TABLE_METADATA_FIELDS, all_tables_field_metadata, output_path_table_metadata)
        self.result_to_csv(APP_METADATA_FIELDS, list(list(d.values()) for d in app_metadata.values()), output_path_app_metadata)


    def get_data(self, unique_data_ids=None, sample=False, output_type='csv', **kwargs):
        """
        Returns a JSON object of the entire data set.

        """
        data_json = None

        if unique_data_ids is None:
            unique_data_ids = self._available_unique_data_ids

        for u in unique_data_ids:
            if (u not in self._available_unique_data_ids):
                logging.info("  The unique_data_id '{}' is not supported by the DhcdApiConn".format(u))

            else:
                result = self.get(self._urls[u], params=self._params[u])

                if result.status_code != 200:
                    err = "An error occurred during request: status {0}"
                    raise Exception(err.format(result.status_code))

                data_xml_root = xml_fromstring(result.text)
                data_xml_records = data_xml_root.findall('record')
                data_json = xml_to_json.data(data_xml_root)

                if output_type == 'stdout':
                    print(json.dumps(data_json, indent=4))

                elif output_type == 'csv':

                    results = [ DhcdResult({e.tag: e.text for e in list(r)}, self._fields[u]).data for r in data_xml_records ]

                    self.result_to_csv(self._fields[u], results, self.output_paths[u])

        # Return last result data set as JSON object
        return data_json


# For testing purposes (running this as a script):
if __name__ == '__main__':
    d = DhcdApiConn()

#    unique_data_ids = ['dhcd_dfd_projects']
    unique_data_ids = None
    sample = False

#    output_type = 'stdout'
    output_type = 'csv'
    db = None

    d.get_data(unique_data_ids, sample, output_type, db=db)


