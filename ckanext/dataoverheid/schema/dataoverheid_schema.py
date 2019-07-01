# encoding: utf-8

"""
Exposes the extensions to the package and resource schemas of CKAN that implement the additional fields used by the
data.overheid.nl web application.
"""

import ckan.plugins.toolkit as tk


def create_schema(original_schema):
    """
    Applies the data.overheid.nl schema to the package and resource create schemas.

    :param original_schema: The original package schema
    :return: The modified package schema
    """
    optional = tk.get_validator('ignore_empty')
    single_value = tk.get_validator('single_value')
    multi_value = tk.get_validator('multi_value')
    string = tk.get_validator('is_string')
    number = tk.get_validator('is_number')
    boolean = tk.get_validator('is_bool')
    date = tk.get_validator('is_date')
    taxonomy = tk.get_validator('taxonomy')
    communities_extractor = tk.get_validator('determine_communities')
    to_extras = tk.get_converter('convert_to_extras')

    original_schema.update({
        '__before':                         [communities_extractor],

        'dataset_quality':                  [optional, single_value, number, to_extras],
        'restrictions_statement':           [optional, single_value, string, to_extras],
        'duplicate_resources':              [optional, single_value, string, to_extras],
        'communities':                      [optional, multi_value(), taxonomy('DONL:Communities'), to_extras]
    })

    original_schema['resources'].update({
        'link_status':                      [optional, single_value, boolean],
        'link_status_last_checked':         [optional, single_value, date('%Y-%m-%dT%H:%M:%S')],
        'is_duplicate_of':                  [optional, single_value, string]
    })

    return original_schema


def update_schema(original_schema):
    """
    Applies the data.overheid.nl schema to the package and resource update schemas.

    :param original_schema: The original package schema
    :return: The modified package schema
    """
    optional = tk.get_validator('ignore_empty')
    single_value = tk.get_validator('single_value')
    multi_value = tk.get_validator('multi_value')
    string = tk.get_validator('is_string')
    number = tk.get_validator('is_number')
    boolean = tk.get_validator('is_bool')
    date = tk.get_validator('is_date')
    taxonomy = tk.get_validator('taxonomy')
    communities_extractor = tk.get_validator('determine_communities')
    to_extras = tk.get_converter('convert_to_extras')

    original_schema.update({
        '__before':                         [communities_extractor],

        'dataset_quality':                  [optional, single_value, number, to_extras],
        'restrictions_statement':           [optional, single_value, string, to_extras],
        'duplicate_resources':              [optional, single_value, string, to_extras],
        'communities':                      [optional, multi_value(), taxonomy('DONL:Communities'), to_extras]
    })

    original_schema['resources'].update({
        'link_status':                      [optional, single_value, boolean],
        'link_status_last_checked':         [optional, single_value, date('%Y-%m-%dT%H:%M:%S')],
        'is_duplicate_of':                  [optional, single_value, string]
    })

    return original_schema


def show_schema(original_schema):
    """
    Applies the data.overheid.nl schema to the package and resource show schemas.

    :param original_schema: The original package schema
    :return: The modified package schema
    """
    optional = tk.get_validator('ignore_empty')
    single_value = tk.get_validator('single_value')
    from_extras = tk.get_converter('convert_from_extras')
    multi_value = tk.get_validator('multi_value')

    original_schema.update({
        'dataset_quality':                  [from_extras, optional, single_value],
        'restrictions_statement':           [from_extras, optional, single_value],
        'duplicate_resources':              [from_extras, optional, single_value],
        'communities':                      [from_extras, optional, multi_value()]
    })

    original_schema['resources'].update({
        'link_status':                      [optional, single_value],
        'link_status_last_checked':         [optional, single_value],
        'is_duplicate_of':                  [optional, single_value]
    })

    return original_schema
