# encoding: utf-8

"""
Exposes functionality which ensures that multivalued properties are correctly send to the Solr
installation.
"""


def transform_multivalued_properties(data_dict):
    """
    Performs several transformations on properties.
    - all multivalued properties are converted from strings to lists
    - all datetime properties are transformed to the Solr datetime format

    :param data_dict: dict, The original dictionary
    :return: dict, The modified dictionary
    """
    for prop in ['alternate_identifier', 'conforms_to', 'related_resource', 'source',
                 'version_notes', 'has_version', 'is_version_of', 'provenance', 'documentation',
                 'sample', 'theme', 'spatial_scheme', 'spatial_value', 'language', 'communities']:
        try:
            data_dict[prop] = data_dict[prop].replace('{', '').replace('}', '').split(',')
        except KeyError:
            continue

    for prop in ['temporal_start', 'temporal_end', 'date_planned', 'issued', 'modified']:
        try:
            data_dict[prop] = u'{0}Z'.format(data_dict[prop])
        except KeyError:
            continue

    for prop in ['language', 'download_url', 'linked_schemas', 'documentation']:
        try:
            for resource in data_dict['resources']:
                resource[prop] = resource[prop].replace('{', '').replace('}', '')
        except KeyError:
            continue

    for prop in ['release_date', 'modification_date']:
        try:
            for resource in data_dict['resources']:
                resource[prop] = u'{0}Z'.format(resource[prop])
        except KeyError:
            continue

    return data_dict
