# encoding: utf-8

"""
Reads and returns values defined in the config.json file located in the root of the
ckanext-dataoverheid extension.
"""


import os
import json
from caching import cached


@cached
def get_controlled_vocabularies():
    """
    Retrieves and returns all the defined controlled vocabularies in a list format. This list
    contains dictionaries, each dictionary represents a controlled vocabulary with the keys 'name',
    'local' and 'online'. The local key defines the filename of the controlled vocabulary as it is
    in the ckanext/dataoverheid/resources/controlled_vocabularies directory. The online key contains
    the URL to the online version of the controlled vocabulary.

    :return: list, A list of dictionaries containing controlled vocabularies
    """
    config_vocabularies = _load_config_file()['controlled_vocabularies']
    vocabularies = {}

    for vocabulary in config_vocabularies:
        vocabularies[vocabulary['name']] = vocabulary

    return vocabularies


@cached
def get_taxonomies():
    """

    :return:
    """
    config_taxonomies = _load_config_file()['taxonomies']
    taxonomies = {}

    for taxonomy in config_taxonomies:
        taxonomies[taxonomy['name']] = taxonomy

    return taxonomies


@cached
def get_communities():
    """

    :return:
    """
    return _load_config_file()['communities']


@cached
def get_all_properties_to_remove():
    """
    Returns a dictionary with the package and resource properties which should be stripped from the package and/or
    resource.

    :return: dict, A dictionary containing two lists of properties to remove
    """
    return {
        'package': get_properties_to_remove(),
        'resource': get_resource_properties_to_remove()
    }


@cached
def get_properties_to_remove():
    """
    Retrieves and returns all the defined properties to remove from the CKAN package dictionary
    before it is returned to the end-user.

    :return: list, A list of strings containing the properties to remove
    """
    return _load_config_file()['properties_to_remove']


@cached
def get_resource_properties_to_remove():
    """
    Retrieves and returns all the defined properties to remove from the CKAN resource dictionary
    before it is returned to the end-user.

    :return: list, A list of strings containing the properties to remove
    """
    return _load_config_file()['resource_properties_to_remove']


@cached
def get_non_open_licenses():
    """
    Retrieves and returns all the licenses which are considered 'non-open'.

    :return: list, A list of license values which are considered 'non-open'
    """
    return _load_config_file()['non_open_licenses']


@cached
def _load_config_file():
    """
    Reads the config.json config file in the root of the ckanext-dataoverheid extension. The result
    of this reading operating is cached for up to 24 hours.

    :return: dict, The contents of the config.json file
    """
    filepath = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.json')

    with open(filepath, 'r') as config_file:
        return json.load(config_file)
