"""
Model for DHCD DFD api
"""


APP_ID = 'bit4kvfmq'


TABLE_ID_MAPPING = {
        'Projects'               : 'bit4krbdh',
        'Properties'             : 'bi4xqgzv4',
        'Units'                  : 'bi5rjybzu',
        'Loans'                  : 'bje8tw7zv',
        'Modifications'          : 'bmdugdvkj',
        'LIHTC Allocations'      : 'bje6i5q6n',
        'Construction Activity'  : 'bje32df5p',
        'Funding Sources'        : 'biwe8ny4f',
        '8609s'                  : 'bmbugpa4q',
        '8610s'                  : 'bk8mpqqqx',
        'Source/Use'             : 'bk5cnab59',
        'AMI Levels'             : 'bi5rib47y',
        'Fiscal Years'           : 'bk8mkqy47',
        'Organizations'          : 'bmhgudsjn',
        'Teams'                  : 'bks6xc8h7',
        'Project Managers'       : 'bknhzjtqb',
        'Funding Increases'      : 'bmmnf2mzm',
        'LIHTC Fees'             : 'bmsjssxp6',
        'LIHTC - BINs'           : 'bms24sdeg',
        'Council Packages'       : 'bmr6b6ipk',
        'Policies and Procedures': 'bma2g4g7a',
        'DHCD Documents'         : 'bknktet3x',
        'Images/Icons'           : 'biw84iuzj'
}


APP_METADATA_FIELDS = [
        'table_name',                   # table name
        'table_dbid',                   # table DBID
        'table_alias',                  # table alias (contains the prefix '_dbid_'
        'key_fid',                      # field ID of the key field
        'default_sort_fid',             # field ID of the default sort field
        'default_sort_order',           # default sort order
        'single_record_name',           # singular version of record name
        'plural_record_name',           # plural version of record name
        'field_metadata_line_start',    # first line of field metadata in table metadata file
        'field_metadata_line_end'       # last line of field metadata in table metadata file
]


TABLE_METADATA_FIELDS = [
        'table_name',                   # table name
        'field_name',                   # field name, derived from the field label by converting all alphabetic characters to lowercase, converting all remaining characters to underscores, and prepending an underscore if the label starts with a digit
        'field_label',                  # field label for forms and reports
        'field_id',                     # field ID (a/k/a fid)
        'field_type',                   # field type
        'base_type',                    # underlying data type
        'appears_by_default',           # indicates whether field appears by default on reports, forms, etc.
        'composite_field_parent_fid',   # for a child/component field of a composite field (e.g. an address), the fid of the parent field
        'composite_field_child_fids',   # for a composite field (e.g. an address), the fid of all child/component fields
        'mode',                         # field mode:  'lookup' for lookup fields, 'virtual' for formula-based or dblink fields, 'summary' for []
        'formula',                      # for a formula-based field (mode=='virtual' and field_type!='dblink' and <formula> value exists), contains the formula used to derive the field's value
        'choices',                      # newline-delimited choices for dropdown fields
        'lookup_target_fid',            # for a lookup field (mode=='lookup' and <lutfid> value exists), contains the fid of the field in the lookup table that this lookup field references
        'lookup_source_fid',            # for a lookup field (mode=='lookup' and <lusfid> value exists), contains the fid of the field in this table that references the lookup table record (usually via its primary key)
        'dblink_target_dbid',           # for a dblink field (mode=='virtual' and field_type=='dblink' and <target_dbid> value exists), contains the dblink's target table dbid
        'dblink_target_fid',            # for a dblink field (mode=='virtual' and field_type=='dblink' and <target_fid> value exists), contains the fid of the field in the dblink's target table that refers to this table
        'dblink_source_fid',            # for a dblink field (mode=='virtual' and field_type=='dblink' and <source_fid> value exists), contains the fid of the field in this table that the dblink's target table field refers to
        'fkey_table_app_dbid',          # for a foreign key field (<mastag> value exists), contains the app DBID of the referenced table
        'fkey_table_alias',             # for a foreign key field (<mastag> value exists), contains the table alias of the referenced table
        'field_help'                    # optional field help description
]


class DhcdResult(object):

    def __init__(self, result, fields):
        self.data = []
        for attr in fields:
            if attr in result:
                value = result.get(attr) or ''
                self.data.append(value)
            else:
                print("WARNING: Field '{}' not found in result.".format(attr))
