# encoding: utf-8


import os
import json
from datetime import datetime
from ckan.lib.redis import connect_to_redis


def get_validation_configuration():
    """
    Retrieves the validation configuration, as its stored in the Redis cache.

    :return: dict, The validation configuration
    """
    _load_config_file()

    return json.loads(redis_conn.get('ckanext.dataoverheid:config.validation'))


def get_dcat_configuration():
    """
    Retrieves the DCAT configuration, as its stored in the Redis cache.

    :return: dict, The DCAT configuration
    """
    _load_config_file()

    return json.loads(redis_conn.get('ckanext.dataoverheid:config.dcat'))


def get_solr_configuration():
    """
    Retrieves the Solr configuration, as its stored in the Redis cache.

    :return: dict, The Solr configuration
    """
    _load_config_file()

    return json.loads(redis_conn.get('ckanext.dataoverheid:config.solr'))


def get_properties_to_remove():
    """
    Retrieves the properties to remove, as they're stored in the Redis cache.

    :return: dict, The properties to remove
    """
    _load_config_file()

    return json.loads(redis_conn.get('ckanext.dataoverheid:config.properties_to_remove'))


def in_list(name, list_type, value):
    """
    Checks whether or not a given value is part of a given list.

    The lists to check against are stored in the Redis instance configured in the CKAN `production.ini` file. So in
    order to check against the list, the list will first be retrieved from Redis.

    :param str name:      The name of the list
    :param str list_type: The type of the list
    :param str value:     The value to search for

    :return: bool, Whether or not the value is contained in the list
    """
    _load_config_file()

    return value in redis_conn.get('ckanext.dataoverheid:{0}.{1}'.format(list_type, name))


def _load_list(name, local_name, list_type='vocabulary'):
    """
    Loads the requested list from the local filesystem. The identifiers of all the entries in the list are put into a
    list, this list is then returned.

    See also: https://waardelijsten.dcat-ap-donl.nl

    Support list_types:
     - vocabulary, found in `'ckanext/dataoverheid/resources/vocabularies/*'`
     - taxonomy, found in `'ckanext/dataoverheid/resources/taxonomies/*'`

    Will raise a Exception under the following conditions:
     - No list is found locally with the given name
     - The local list contains content that could not be parsed as valid JSON

    :param str name:       The name of the list to load
    :param str local_name: The name of the list on the filesystem
    :param str list_type:  The type of list to load

    :return: list, The entries of the loaded list
    """
    try:
        list_type = 'vocabularies' if list_type == 'vocabulary' else 'taxonomies'
        filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', list_type, local_name)

        with open(filepath, 'rb') as file_contents:
            parsed = json.loads(file_contents.read())

            try:
                return [block['id'] for block in parsed] if name == 'Overheid:License' else parsed.keys()
            except KeyError:
                raise Exception('{0} is malformed;'.format(name))
    except KeyError:
        raise Exception('the requested vocabulary [{0}] does not exist or is not supported'.format(name))


def _load_config_file():
    """
    Loads the contents from the ckanext-dataoverheid configuration file and stores it in Redis for later use.
    Additionally all the vocabularies and taxonomies used in DCAT-AP-DONL are stored in Redis so that they can be made
    available to CKAN during the package validation process.

    The Redis cache will be updated once every 24 hours on the first request of the day.

    :return: void
    """
    current_date = str(datetime.strftime(datetime.now(), '%Y%m%d'))

    if current_date == redis_conn.get('ckanext.dataoverheid:config._cache_date'):
        return

    filepath = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'config.json')

    with open(filepath, 'r') as config_file:
        contents = json.load(config_file)

        redis_conn.set('ckanext.dataoverheid:config._cache_date', current_date)
        redis_conn.set('ckanext.dataoverheid:config.validation', json.dumps(contents.get('validation')))
        redis_conn.set('ckanext.dataoverheid:config.dcat', json.dumps(contents.get('dcat')))
        redis_conn.set('ckanext.dataoverheid:config.solr', json.dumps(contents.get('solr')))
        redis_conn.set('ckanext.dataoverheid:config.properties_to_remove',
                       json.dumps(contents.get('properties_to_remove')))

        [redis_conn.set('ckanext.dataoverheid:vocabulary.{0}'.format(key),
                        json.dumps(_load_list(key, voc['local'], 'vocabulary')))
         for key, voc in contents.get('validation')['vocabularies'].iteritems()]

        [redis_conn.set('ckanext.dataoverheid:taxonomy.{0}'.format(key),
                        json.dumps(_load_list(key, tax['local'], 'taxonomy')))
         for key, tax in contents.get('validation')['taxonomies'].iteritems()]


redis_conn = connect_to_redis()
_load_config_file()
