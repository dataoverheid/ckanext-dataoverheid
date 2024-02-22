# encoding: utf-8


from __future__ import absolute_import
from .config import get_config


def transform_multivalued_properties(data_dict):
    """
    Performs several transformations on properties in a given dictionary.
    - all multivalued properties are converted from strings to lists
    - all datetime properties are transformed to the Solr datetime format

    :param dict[Any, Any] data_dict: The original dictionary
    :rtype: dict[Any, Any]
    """
    transformations = get_config('transformations')
    replacements = (('{', ''), ('}', ''))

    for prop in transformations['package']['multi_valued']:
        try:
            for item in replacements:
                data_dict[prop] = data_dict[prop].replace(*item)

            data_dict[prop] = data_dict[prop].split(',')
        except KeyError:
            continue

    for prop in transformations['package']['date']:
        try:
            data_dict[prop] = '{0}Z'.format(data_dict[prop])
        except KeyError:
            continue

    for prop in transformations['resource']['multi_valued']:
        try:
            for resource in data_dict['resources']:
                for item in replacements:
                    resource[prop] = resource[prop].replace(*item)
        except KeyError:
            continue

    for prop in transformations['resource']['date']:
        try:
            for resource in data_dict['resources']:
                resource[prop] = '{0}Z'.format(resource[prop])
        except KeyError:
            continue

    return data_dict


def remove_properties(data_dict):
    """
    Removes keys from a given dictionary. The keys that are removed are defined
    in the `'config.json'` file in the root of this extension under the keys
    `'properties_to_remove'` and `'resource_properties_to_remove'`.

    This allows the `ckanext-dataoverheid` extension to remove the properties
    used by the CKAN core which provide no value to the CKAN installation
    running the `ckanext-dataoverheid` extension.

    :param dict[Any, Any] data_dict: The dictionary representing a CKAN package
    :rtype: None
    """
    properties_to_remove = get_config('properties_to_remove')
    [data_dict.pop(prop, None) for prop in properties_to_remove['package']]

    try:
        [[resource.pop(prop, None) for prop in properties_to_remove['resource']]
         for resource in data_dict['resources']]
    except KeyError:
        pass

    try:
        [[tag.pop(prop, None) for prop in properties_to_remove['tag']]
         for tag in data_dict['tags']]
    except KeyError:
        pass

    try:
        [data_dict['organization'].pop(prop, None)
         for prop in properties_to_remove['organization']
         if prop in data_dict['organization']]
    except KeyError:
        pass

    try:
        [[group.pop(prop, None) for prop in properties_to_remove['group']]
         for group in data_dict['groups']]
    except KeyError:
        pass
