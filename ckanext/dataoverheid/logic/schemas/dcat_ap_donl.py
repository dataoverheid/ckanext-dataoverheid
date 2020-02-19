# encoding: utf-8


import ckan.plugins.toolkit as tk


def create_schema(original_schema):
    """
    Applies the DCAT-AP-DONL 1.1 schema to the package and resource create schemas.

    :param dict original_schema: The original package schema

    :return: dict, The modified package schema
    """
    mandatory = tk.get_validator('not_empty')
    recommended = tk.get_validator('ignore_empty')
    optional = tk.get_validator('ignore_empty')
    to_extras = tk.get_converter('convert_to_extras')
    single_value = tk.get_validator('single_value')
    multi_value = tk.get_validator('multi_value')
    string = tk.get_validator('is_string')
    boolean = tk.get_validator('is_bool')
    uri = tk.get_validator('is_uri')
    date = tk.get_validator('is_date')
    number = tk.get_validator('is_number')
    controlled_vocabulary = tk.get_validator('controlled_vocabulary')
    default = tk.get_converter('default_conversion')
    res_to_string = tk.get_converter('convert_list_to_string')
    contact_point = tk.get_validator('contact_point')
    temporal = tk.get_validator('temporal')
    legal_foundation = tk.get_validator('legal_foundation')
    spatial = tk.get_validator('spatial')
    rights = tk.get_validator('rights')
    checksum = tk.get_validator('checksum')
    date_planned = tk.get_validator('date_planned')

    original_schema.update({
        'title':                    [mandatory, single_value, string],
        'notes':                    [mandatory, single_value, string],
        'url':                      [optional, single_value, uri],
        'theme':                    [mandatory, multi_value(), controlled_vocabulary('Overheid:Taxonomiebeleidsagenda'),
                                     to_extras],

        'identifier':               [mandatory, single_value, uri, to_extras],
        'alternate_identifier':     [recommended, multi_value(), uri, to_extras],
        'source_catalog':           [recommended, single_value, controlled_vocabulary('DONL:Catalogs'), to_extras],

        'authority':                [mandatory, single_value, controlled_vocabulary('DONL:Organization'), to_extras],
        'publisher':                [mandatory, single_value, controlled_vocabulary('DONL:Organization'), to_extras],
        'contact_point_name':       [mandatory, single_value, string, to_extras],
        'contact_point_title':      [recommended, single_value, string, to_extras],
        'contact_point_address':    [recommended, single_value, string, to_extras],
        'contact_point_email':      [recommended, single_value, string, to_extras],
        'contact_point_website':    [recommended, single_value, uri, to_extras],
        'contact_point_phone':      [recommended, single_value, string, to_extras],

        'metadata_language':        [mandatory, single_value, controlled_vocabulary('DONL:Language'), to_extras],
        'language':                 [mandatory, multi_value(), controlled_vocabulary('DONL:Language'), to_extras],

        'license_id':               [mandatory, single_value, controlled_vocabulary('Overheid:License')],
        'access_rights':            [recommended, single_value, controlled_vocabulary('Overheid:Openbaarheidsniveau'),
                                     to_extras],

        'temporal_label':           [recommended, single_value, string, to_extras],
        'temporal_start':           [recommended, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'temporal_end':             [recommended, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],

        'spatial_scheme':           [recommended, multi_value(allow_duplicates=True),
                                     controlled_vocabulary('Overheid:SpatialScheme'), to_extras],
        'spatial_value':            [recommended, multi_value(), to_extras],

        'legal_foundation_label':   [recommended, single_value, string, to_extras],
        'legal_foundation_ref':     [recommended, single_value, string, to_extras],
        'legal_foundation_uri':     [recommended, single_value, uri, to_extras],

        'dataset_status':           [default(u'http://data.overheid.nl/status/beschikbaar'), single_value,
                                     controlled_vocabulary('Overheid:DatasetStatus'), to_extras],
        'date_planned':             [optional, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'issued':                   [recommended, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'modified':                 [mandatory, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'frequency':                [recommended, single_value, controlled_vocabulary('Overheid:Frequency'), to_extras],

        'documentation':            [optional, multi_value(), uri, to_extras],
        'sample':                   [optional, multi_value(), uri, to_extras],
        'provenance':               [optional, multi_value(), uri, to_extras],

        'version':                  [optional, single_value, string],
        'version_notes':            [optional, multi_value(), string, to_extras],

        'is_version_of':            [optional, multi_value(), uri, to_extras],
        'has_version':              [optional, multi_value(), uri, to_extras],
        'source':                   [optional, multi_value(), uri, to_extras],
        'related_resource':         [optional, multi_value(), uri, to_extras],
        'conforms_to':              [optional, multi_value(), uri, to_extras],

        'changetype':               [default(':created', force=True), controlled_vocabulary('ADMS:Changetype'),
                                     to_extras],

        'high_value':               [default(False), single_value, boolean, to_extras],
        'referentie_data':          [default(False), single_value, boolean, to_extras],
        'basis_register':           [default(False), single_value, boolean, to_extras],

        'national_coverage':        [default(False), single_value, boolean, to_extras],

        '__after':                  [contact_point, temporal, legal_foundation, spatial, date_planned, rights]
    })

    original_schema['resources'].update({
        'url':                      [mandatory, single_value, string],
        'download_url':             [recommended, multi_value(), uri, res_to_string],
        'documentation':            [recommended, multi_value(), uri, res_to_string],
        'linked_schemas':           [recommended, multi_value(), uri, res_to_string],

        'name':                     [mandatory, single_value, string],
        'description':              [mandatory, single_value, string],
        'status':                   [recommended, single_value, controlled_vocabulary('ADMS:DistributieStatus')],

        'metadata_language':        [mandatory, single_value, controlled_vocabulary('DONL:Language')],
        'language':                 [mandatory, multi_value(), controlled_vocabulary('DONL:Language'), res_to_string],

        'license_id':               [mandatory, single_value, controlled_vocabulary('Overheid:License')],
        'rights':                   [recommended, single_value, string],

        'format':                   [mandatory, single_value, controlled_vocabulary('MDR:FiletypeNAL')],
        'media_type':               [recommended, single_value, controlled_vocabulary('IANA:Mediatypes')],

        'size':                     [recommended, single_value, number],

        'hash':                     [optional, single_value, string],
        'hash_algorithm':           [optional, single_value, string],

        'release_date':             [recommended, single_value, date('%Y-%m-%dT%H:%M:%S')],
        'modification_date':        [recommended, single_value, date('%Y-%m-%dT%H:%M:%S')],

        '__after':                  [checksum]
    })

    return original_schema


def update_schema(original_schema):
    """
    Applies the DCAT-AP-DONL 1.1 schema to the package and resource update schemas.

    :param dict original_schema: The original package schema

    :return: dict, The modified package schema
    """
    mandatory = tk.get_validator('not_empty')
    recommended = tk.get_validator('ignore_empty')
    optional = tk.get_validator('ignore_empty')
    to_extras = tk.get_converter('convert_to_extras')
    single_value = tk.get_validator('single_value')
    multi_value = tk.get_validator('multi_value')
    string = tk.get_validator('is_string')
    boolean = tk.get_validator('is_bool')
    uri = tk.get_validator('is_uri')
    date = tk.get_validator('is_date')
    number = tk.get_validator('is_number')
    controlled_vocabulary = tk.get_validator('controlled_vocabulary')
    default = tk.get_converter('default_conversion')
    res_to_string = tk.get_converter('convert_list_to_string')
    contact_point = tk.get_validator('contact_point')
    temporal = tk.get_validator('temporal')
    legal_foundation = tk.get_validator('legal_foundation')
    spatial = tk.get_validator('spatial')
    rights = tk.get_validator('rights')
    checksum = tk.get_validator('checksum')
    date_planned = tk.get_validator('date_planned')

    original_schema.update({
        'title':                    [mandatory, single_value, string],
        'notes':                    [mandatory, single_value, string],
        'url':                      [optional, single_value, uri],
        'theme':                    [mandatory, multi_value(), controlled_vocabulary('Overheid:Taxonomiebeleidsagenda'),
                                     to_extras],

        'identifier':               [mandatory, single_value, uri, to_extras],
        'alternate_identifier':     [recommended, multi_value(), uri, to_extras],
        'source_catalog':           [recommended, single_value, controlled_vocabulary('DONL:Catalogs'), to_extras],

        'authority':                [mandatory, single_value, controlled_vocabulary('DONL:Organization'), to_extras],
        'publisher':                [mandatory, single_value, controlled_vocabulary('DONL:Organization'), to_extras],
        'contact_point_name':       [mandatory, single_value, string, to_extras],
        'contact_point_title':      [recommended, single_value, string, to_extras],
        'contact_point_address':    [recommended, single_value, string, to_extras],
        'contact_point_email':      [recommended, single_value, string, to_extras],
        'contact_point_website':    [recommended, single_value, uri, to_extras],
        'contact_point_phone':      [recommended, single_value, string, to_extras],

        'metadata_language':        [mandatory, single_value, controlled_vocabulary('DONL:Language'), to_extras],
        'language':                 [mandatory, multi_value(), controlled_vocabulary('DONL:Language'), to_extras],

        'license_id':               [mandatory, single_value, controlled_vocabulary('Overheid:License')],
        'access_rights':            [recommended, single_value, controlled_vocabulary('Overheid:Openbaarheidsniveau'),
                                     to_extras],

        'temporal_label':           [recommended, single_value, string, to_extras],
        'temporal_start':           [recommended, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'temporal_end':             [recommended, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],

        'spatial_scheme':           [recommended, multi_value(allow_duplicates=True),
                                     controlled_vocabulary('Overheid:SpatialScheme'), to_extras],
        'spatial_value':            [recommended, multi_value(), to_extras],

        'legal_foundation_label':   [recommended, single_value, string, to_extras],
        'legal_foundation_ref':     [recommended, single_value, string, to_extras],
        'legal_foundation_uri':     [recommended, single_value, uri, to_extras],

        'dataset_status':           [recommended, single_value, controlled_vocabulary('Overheid:DatasetStatus'),
                                     to_extras],
        'date_planned':             [optional, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'issued':                   [recommended, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'modified':                 [mandatory, single_value, date('%Y-%m-%dT%H:%M:%S'), to_extras],
        'frequency':                [recommended, single_value, controlled_vocabulary('Overheid:Frequency'),
                                     to_extras],

        'documentation':            [optional, multi_value(), uri, to_extras],
        'sample':                   [optional, multi_value(), uri, to_extras],
        'provenance':               [optional, multi_value(), uri, to_extras],

        'version':                  [optional, single_value, string],
        'version_notes':            [optional, multi_value(), string, to_extras],

        'is_version_of':            [optional, multi_value(), uri, to_extras],
        'has_version':              [optional, multi_value(), uri, to_extras],
        'source':                   [optional, multi_value(), uri, to_extras],
        'related_resource':         [optional, multi_value(), uri, to_extras],
        'conforms_to':              [optional, multi_value(), uri, to_extras],

        'changetype':               [default(':updated', force=True), controlled_vocabulary('ADMS:Changetype'),
                                     to_extras],

        'high_value':               [default(False), single_value, boolean, to_extras],
        'referentie_data':          [default(False), single_value, boolean, to_extras],
        'basis_register':           [default(False), single_value, boolean, to_extras],

        'national_coverage':        [default(False), single_value, boolean, to_extras],

        '__after':                  [contact_point, temporal, legal_foundation, spatial, date_planned, rights]
    })

    original_schema['resources'].update({
        'url':                      [mandatory, single_value, string],
        'download_url':             [recommended, multi_value(), uri, res_to_string],
        'documentation':            [recommended, multi_value(), uri, res_to_string],
        'linked_schemas':           [recommended, multi_value(), uri, res_to_string],

        'name':                     [mandatory, single_value, string],
        'description':              [mandatory, single_value, string],
        'status':                   [recommended, single_value, controlled_vocabulary('ADMS:DistributieStatus')],

        'metadata_language':        [mandatory, single_value, controlled_vocabulary('DONL:Language')],
        'language':                 [mandatory, multi_value(), controlled_vocabulary('DONL:Language'), res_to_string],

        'license_id':               [mandatory, single_value, controlled_vocabulary('Overheid:License')],
        'rights':                   [recommended, single_value, string],

        'format':                   [mandatory, single_value, controlled_vocabulary('MDR:FiletypeNAL')],
        'media_type':               [recommended, single_value, controlled_vocabulary('IANA:Mediatypes')],

        'size':                     [recommended, single_value, number],

        'hash':                     [optional, single_value, string],
        'hash_algorithm':           [optional, single_value, string],

        'release_date':             [recommended, single_value, date('%Y-%m-%dT%H:%M:%S')],
        'modification_date':        [recommended, single_value, date('%Y-%m-%dT%H:%M:%S')],

        '__after':                  [checksum]
    })

    return original_schema


def show_schema(original_schema):
    """
    Applies the DCAT-AP-DONL 1.1 schema to the package and resource show schemas.

    :param dict original_schema: The original package schema

    :return: dict, The modified package schema
    """
    mandatory = tk.get_validator('not_empty')
    recommended = tk.get_validator('ignore_empty')
    optional = tk.get_validator('ignore_empty')
    from_extras = tk.get_validator('convert_from_extras')
    single_value = tk.get_validator('single_value')
    multi_value = tk.get_validator('multi_value')

    original_schema.update({
        'title':                    [mandatory, single_value],
        'notes':                    [mandatory, single_value],
        'url':                      [optional, single_value],
        'theme':                    [from_extras, mandatory, multi_value()],

        'identifier':               [from_extras, mandatory, single_value],
        'alternate_identifier':     [from_extras, recommended, multi_value()],
        'source_catalog':           [from_extras, recommended, single_value],

        'authority':                [from_extras, mandatory, single_value],
        'publisher':                [from_extras, mandatory, single_value],
        'contact_point_name':       [from_extras, mandatory, single_value],
        'contact_point_title':      [from_extras, recommended, single_value],
        'contact_point_address':    [from_extras, recommended, single_value],
        'contact_point_email':      [from_extras, recommended, single_value],
        'contact_point_website':    [from_extras, recommended, single_value],
        'contact_point_phone':      [from_extras, recommended, single_value],

        'metadata_language':        [from_extras, mandatory, single_value],
        'language':                 [from_extras, mandatory, multi_value()],

        'license_id':               [mandatory, single_value],
        'access_rights':            [from_extras, recommended, single_value],

        'temporal_label':           [from_extras, recommended, single_value],
        'temporal_start':           [from_extras, recommended, single_value],
        'temporal_end':             [from_extras, recommended, single_value],

        'spatial_scheme':           [from_extras, recommended, multi_value(allow_duplicates=True)],
        'spatial_value':            [from_extras, recommended, multi_value()],

        'legal_foundation_label':   [from_extras, recommended, single_value],
        'legal_foundation_ref':     [from_extras, recommended, single_value],
        'legal_foundation_uri':     [from_extras, recommended, single_value],

        'dataset_status':           [from_extras, recommended, single_value],
        'date_planned':             [from_extras, optional, single_value],
        'issued':                   [from_extras, recommended, single_value],
        'modified':                 [from_extras, mandatory, single_value],
        'frequency':                [from_extras, recommended, single_value],

        'documentation':            [from_extras, optional, multi_value()],
        'sample':                   [from_extras, optional, multi_value()],
        'provenance':               [from_extras, optional, multi_value()],

        'version':                  [optional, single_value],
        'version_notes':            [from_extras, optional, multi_value()],

        'is_version_of':            [from_extras, optional, multi_value()],
        'has_version':              [from_extras, optional, multi_value()],
        'source':                   [from_extras, optional, multi_value()],
        'related_resource':         [from_extras, optional, multi_value()],
        'conforms_to':              [from_extras, optional, multi_value()],

        'high_value':               [from_extras, recommended, single_value],
        'referentie_data':          [from_extras, recommended, single_value],
        'basis_register':           [from_extras, recommended, single_value],

        'national_coverage':        [from_extras, recommended, single_value],

        'changetype':               [from_extras, recommended, single_value]
    })

    original_schema['resources'].update({
        'url':                      [mandatory, single_value],
        'download_url':             [recommended, multi_value()],
        'documentation':            [recommended, multi_value()],
        'linked_schemas':           [recommended, multi_value()],

        'name':                     [mandatory, single_value],
        'description':              [mandatory, single_value],
        'status':                   [recommended, single_value],

        'metadata_language':        [mandatory, single_value],
        'language':                 [mandatory, multi_value()],

        'license_id':               [mandatory, single_value],
        'rights':                   [recommended, single_value],

        'format':                   [mandatory, single_value],
        'media_type':               [recommended, single_value],

        'size':                     [recommended, single_value],

        'hash':                     [optional, single_value],
        'hash_algorithm':           [optional, single_value],

        'release_date':             [recommended, single_value],
        'modification_date':        [recommended, single_value]
    })

    return original_schema
