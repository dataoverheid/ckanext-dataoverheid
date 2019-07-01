# encoding: utf-8

"""
Exposes functionality that certain data types to be converted to other data types given certain conditions.
"""


from ckanext.dataoverheid.helper import get_all_properties_to_remove


def convert_string_to_list(key, data, errors, context):
    """
    Converts a given property to a list, assuming the property has a value and that the value is currently a string
    surrounded with curly brackets.

    :param key: The key of the property
    :param data: The dictionary containing the property
    :param errors: The dictionary containing the validation errors of the data dictionary
    :param context: The CKAN context of the current execution
    :return: tuple, dict, dict, dict The original, possibly modified, arguments
    """
    value = data.get(key, None)

    if not value or not isinstance(value, basestring) or not value.startswith('{') or not value.endswith('}'):
        return key, data, errors, context

    value = value.replace('"', '')
    data[key] = value[1:len(value)-1].split(',')

    return key, data, errors, context


def convert_list_to_string(key, data, errors, context):
    """
    Converts a given property to a string, assuming the property has a value and that the value is currently a list. The
    converted string will be surrounded by curly brackets.

    :param key: The key of the property
    :param data: The dictionary containing the property
    :param errors: The dictionary containing the validation errors of the data dictionary
    :param context: The CKAN context of the current execution
    :return: tuple, dict, dict, dict The original, possibly modified, arguments
    """
    value = data.get(key, None)

    if not value or not isinstance(value, list):
        return key, data, errors, context

    data[key] = '{' + ','.join(map(str, value)) + '}'

    return key, data, errors, context


def remove_properties(data_dict):
    """
    Removes keys from a given dictionary. The keys that are removed are defined in the config.json file in the root of
    this extension under the keys 'properties_to_remove' and 'resource_properties_to_remove'.

    :param data_dict: The dictionary to remove the keys from
    :return: The, possibly modified, original dictionary
    """
    properties_to_remove = get_all_properties_to_remove()

    for prop in properties_to_remove['package']:
        data_dict.pop(prop, None)

    if 'resources' in data_dict:
        for resource in data_dict['resources']:
            for prop in properties_to_remove['resource']:
                resource.pop(prop, None)

    return data_dict
