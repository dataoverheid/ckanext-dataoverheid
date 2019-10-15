# encoding: utf-8


from config import get_properties_to_remove


def transform_multivalued_properties(data_dict):
    """
    Performs several transformations on properties in a given dictionary.
    - all multivalued properties are converted from strings to lists
    - all datetime properties are transformed to the Solr datetime format

    :param dict data_dict: The original dictionary

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


def remove_properties(data_dict):
    """
    Removes keys from a given dictionary. The keys that are removed are defined in the `'config.json'` file in the root
    of this extension under the keys `'properties_to_remove'` and `'resource_properties_to_remove'`.

    This allows the `ckanext-dataoverheid` extension to remove the properties used by the CKAN core which provide no
    value to the CKAN installation running the `ckanext-dataoverheid` extension.

    :param dict data_dict: The dictionary representing a CKAN package

    :return void
    """
    properties_to_remove = get_properties_to_remove()
    [data_dict.pop(prop, None) for prop in properties_to_remove['package']]

    try:
        [[resource.pop(prop, None) for prop in properties_to_remove['resource']] for resource in data_dict['resources']]
    except KeyError:
        pass

    try:
        [[tag.pop(prop, None) for prop in properties_to_remove['tag']] for tag in data_dict['tags']]
    except KeyError:
        pass

    try:
        [data_dict['organization'].pop(prop, None) for prop in properties_to_remove['organization']
         if prop in data_dict['organization']]
    except KeyError:
        pass

    try:
        [[group.pop(prop, None) for prop in properties_to_remove['group']]
         for group in data_dict['groups']]
    except KeyError:
        pass
