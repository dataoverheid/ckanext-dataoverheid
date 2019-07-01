# encoding: utf-8

"""
Exposes value conversion methods that perform operations on specified keys in dictionaries.
"""


from default_converter import default
from property_conversion import remove_properties, convert_list_to_string, convert_string_to_list


def get_all():
    """
    Get and return all the defined converter methods.

    :return: dict, A dictionary containing all the converter methods
    """
    return {
        'convert_string_to_list': convert_string_to_list,
        'convert_list_to_string': convert_list_to_string,
        'default_conversion':     default
    }
