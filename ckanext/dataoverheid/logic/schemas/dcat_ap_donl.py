# encoding: utf-8


import ckan.plugins.toolkit as tk


def create_schema(original_schema):
    """
    Applies the DCAT-AP-DONL 1.1 schema to the package and resource create
    schemas.

    :param dict[str, Any] original_schema: The original package schema
    :rtype: dict[str, Any]
    :return: The modified package schema
    """
    return _mutate_schema(original_schema, ':created')


def update_schema(original_schema):
    """
    Applies the DCAT-AP-DONL 1.1 schema to the package and resource update
    schemas.

    :param dict[str, Any] original_schema: The original package schema
    :rtype: dict[str, Any]
    :return: The modified package schema
    """
    return _mutate_schema(original_schema, ':updated')


def show_schema(original_schema):
    """
    Applies the DCAT-AP-DONL 1.1 schema to the package and resource show
    schemas.

    :param dict[str, Any] original_schema: The original package schema
    :rtype: dict[str, Any]
    :return: The modified package schema
    """
    mandatory = tk.get_validator('not_empty')
    recommended = tk.get_validator('ignore_empty')
    optional = tk.get_validator('ignore_empty')
    extras = tk.get_validator('convert_from_extras')
    single_value = tk.get_validator('single_value')
    multi_value = tk.get_validator('multi_value')

    original_schema.update({
        'title':                    [mandatory, single_value],
        'notes':                    [mandatory, single_value],
        'url':                      [optional, single_value],
        'theme':                    [extras, mandatory, multi_value()],

        'identifier':               [extras, mandatory, single_value],
        'alternate_identifier':     [extras, recommended, multi_value()],
        'source_catalog':           [extras, recommended, single_value],

        'authority':                [extras, mandatory, single_value],
        'publisher':                [extras, mandatory, single_value],
        'contact_point_name':       [extras, mandatory, single_value],
        'contact_point_title':      [extras, recommended, single_value],
        'contact_point_address':    [extras, recommended, single_value],
        'contact_point_email':      [extras, recommended, single_value],
        'contact_point_website':    [extras, recommended, single_value],
        'contact_point_phone':      [extras, recommended, single_value],

        'metadata_language':        [extras, mandatory, single_value],
        'language':                 [extras, mandatory, multi_value()],

        'license_id':               [mandatory, single_value],
        'access_rights':            [extras, recommended, single_value],

        'temporal_label':           [extras, recommended, single_value],
        'temporal_start':           [extras, recommended, single_value],
        'temporal_end':             [extras, recommended, single_value],

        'spatial_scheme':           [extras, recommended,
                                     multi_value(allow_duplicates=True)],
        'spatial_value':            [extras, recommended, multi_value()],

        'legal_foundation_label':   [extras, recommended, single_value],
        'legal_foundation_ref':     [extras, recommended, single_value],
        'legal_foundation_uri':     [extras, recommended, single_value],

        'dataset_status':           [extras, recommended, single_value],
        'date_planned':             [extras, optional, single_value],
        'issued':                   [extras, recommended, single_value],
        'modified':                 [extras, mandatory, single_value],
        'frequency':                [extras, recommended, single_value],

        'documentation':            [extras, optional, multi_value()],
        'sample':                   [extras, optional, multi_value()],
        'provenance':               [extras, optional, multi_value()],

        'version':                  [optional, single_value],
        'version_notes':            [extras, optional, multi_value()],

        'is_version_of':            [extras, optional, multi_value()],
        'has_version':              [extras, optional, multi_value()],
        'source':                   [extras, optional, multi_value()],
        'related_resource':         [extras, optional, multi_value()],
        'conforms_to':              [extras, optional, multi_value()],

        'high_value':               [extras, recommended, single_value],
        'referentie_data':          [extras, recommended, single_value],
        'basis_register':           [extras, recommended, single_value],

        'national_coverage':        [extras, recommended, single_value],

        'changetype':               [extras, recommended, single_value]
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
        'modification_date':        [recommended, single_value],

        'distribution_type':        [recommended, single_value]
    })

    return original_schema


def _mutate_schema(original_schema, default_changetype):
    """
    Applies the DCAT-AP-DONL 1.1 schema to the package and resource update
    schemas.

    :param dict[str, Any] original_schema: The original package schema
    :param str default_changetype: The default ADMS:Changetype value
    :rtype: dict[str, Any]
    :return: The modified package schema
    """
    dataset_status_default = 'http://data.overheid.nl/status/beschikbaar'
    date_format = '%Y-%m-%dT%H:%M:%S'
    mandatory = tk.get_validator('not_empty')
    recommended = tk.get_validator('ignore_empty')
    optional = tk.get_validator('ignore_empty')
    extras = tk.get_converter('convert_to_extras')
    single_value = tk.get_validator('single_value')
    multi_value = tk.get_validator('multi_value')
    string = tk.get_validator('is_string')
    boolean = tk.get_validator('is_bool')
    uri = tk.get_validator('is_uri')
    date = tk.get_validator('is_date')
    number = tk.get_validator('is_number')
    cv = tk.get_validator('controlled_vocabulary')
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
        'theme':                    [mandatory, multi_value(),
                                     cv('Overheid:Taxonomiebeleidsagenda'),
                                     extras],

        'identifier':               [mandatory, single_value, uri, extras],
        'alternate_identifier':     [recommended, multi_value(), uri, extras],
        'source_catalog':           [recommended, single_value,
                                     cv('DONL:Catalogs'), extras],

        'authority':                [mandatory, single_value,
                                     cv('DONL:Organization'), extras],
        'publisher':                [mandatory, single_value,
                                     cv('DONL:Organization'), extras],
        'contact_point_name':       [mandatory, single_value, string, extras],
        'contact_point_title':      [recommended, single_value, string, extras],
        'contact_point_address':    [recommended, single_value, string, extras],
        'contact_point_email':      [recommended, single_value, string, extras],
        'contact_point_website':    [recommended, single_value, uri, extras],
        'contact_point_phone':      [recommended, single_value, string, extras],

        'metadata_language':        [mandatory, single_value,
                                     cv('DONL:Language'), extras],
        'language':                 [mandatory, multi_value(),
                                     cv('DONL:Language'), extras],

        'license_id':               [mandatory, single_value,
                                     cv('DONL:License')],
        'access_rights':            [recommended, single_value,
                                     cv('Overheid:Openbaarheidsniveau'),
                                     extras],

        'temporal_label':           [recommended, single_value, string, extras],
        'temporal_start':           [recommended, single_value,
                                     date(date_format), extras],
        'temporal_end':             [recommended, single_value,
                                     date(date_format), extras],

        'spatial_scheme':           [recommended,
                                     multi_value(allow_duplicates=True),
                                     cv('Overheid:SpatialScheme'), extras],
        'spatial_value':            [recommended, multi_value(), extras],

        'legal_foundation_label':   [recommended, single_value, string, extras],
        'legal_foundation_ref':     [recommended, single_value, string, extras],
        'legal_foundation_uri':     [recommended, single_value, uri, extras],

        'dataset_status':           [default(dataset_status_default),
                                     single_value, cv('Overheid:DatasetStatus'),
                                     extras],
        'date_planned':             [optional, single_value,
                                     date(date_format), extras],
        'issued':                   [recommended, single_value,
                                     date(date_format), extras],
        'modified':                 [mandatory, single_value,
                                     date(date_format), extras],
        'frequency':                [recommended, single_value,
                                     cv('Overheid:Frequency'), extras],

        'documentation':            [optional, multi_value(), uri, extras],
        'sample':                   [optional, multi_value(), uri, extras],
        'provenance':               [optional, multi_value(), uri, extras],

        'version':                  [optional, single_value, string],
        'version_notes':            [optional, multi_value(), string, extras],

        'is_version_of':            [optional, multi_value(), uri, extras],
        'has_version':              [optional, multi_value(), uri, extras],
        'source':                   [optional, multi_value(), uri, extras],
        'related_resource':         [optional, multi_value(), uri, extras],
        'conforms_to':              [optional, multi_value(), uri, extras],

        'changetype':               [default(default_changetype, force=True),
                                     cv('ADMS:Changetype'), extras],

        'high_value':               [default(False), single_value, boolean,
                                     extras],
        'referentie_data':          [default(False), single_value, boolean,
                                     extras],
        'basis_register':           [default(False), single_value, boolean,
                                     extras],
        'national_coverage':        [default(False), single_value, boolean,
                                     extras],

        '__after':                  [contact_point, temporal, legal_foundation,
                                     spatial, date_planned, rights]
    })

    original_schema['resources'].update({
        'url':                      [mandatory, single_value, string],
        'download_url':             [recommended, multi_value(), uri,
                                     res_to_string],
        'documentation':            [recommended, multi_value(), uri,
                                     res_to_string],
        'linked_schemas':           [recommended, multi_value(), uri,
                                     res_to_string],

        'name':                     [mandatory, single_value, string],
        'description':              [mandatory, single_value, string],
        'status':                   [recommended, single_value,
                                     cv('ADMS:DistributieStatus')],

        'metadata_language':        [mandatory, single_value,
                                     cv('DONL:Language')],
        'language':                 [mandatory, multi_value(),
                                     cv('DONL:Language'), res_to_string],

        'license_id':               [mandatory, single_value,
                                     cv('DONL:License')],
        'rights':                   [recommended, single_value, string],

        'format':                   [mandatory, single_value,
                                     cv('MDR:FiletypeNAL')],
        'media_type':               [recommended, single_value,
                                     cv('IANA:Mediatypes')],

        'size':                     [recommended, single_value, number],

        'hash':                     [optional, single_value, string],
        'hash_algorithm':           [optional, single_value, string],

        'release_date':             [recommended, single_value,
                                     date(date_format)],
        'modification_date':        [recommended, single_value,
                                     date(date_format)],

        'distribution_type':        [recommended, single_value,
                                     cv('DONL:DistributionType')],

        '__after':                  [checksum]
    })

    return original_schema
