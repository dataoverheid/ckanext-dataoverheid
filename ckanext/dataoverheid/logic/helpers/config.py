# encoding: utf-8


from builtins import str
import os
import json
from datetime import datetime
from ckan.lib.redis import connect_to_redis


def get_config(config_name):
    """
    Retrieves a specific section of the config by its name. The config is
    retrieved from Redis, as it is cached there for up to 24 hours.

    :param str config_name: the name of the config key
    :rtype: dict[str, list of str|dict[str, list of str|dict[str, dict]]
    """
    _load_config_file()

    return json.loads(redis_conn.get(config_key + config_name))


def in_list(name, list_type, value):
    """
    Checks whether or not a given value is part of a given list.

    The lists to check against are stored in the Redis instance configured in
    the CKAN `production.ini` file. So in order to check against the list, the
    list will first be retrieved from Redis.

    :param str name: The name of the list
    :param str list_type: The type of the list
    :param str value: The value to search for
    :rtype: bool
    :return: Whether or not the value is contained in the list
    """
    _load_config_file()

    return value in json.loads(
        redis_conn.get(redis_key + list_type + '.' + name)
    )


def _load_list(name, local_name, list_type='vocabulary'):
    """
    Loads the requested list from the local filesystem. The identifiers of all
    the entries in the list are put into a list, this list is then returned.

    See also: https://waardelijsten.dcat-ap-donl.nl

    Support list_types:
     - vocabulary, found in `'ckanext/dataoverheid/resources/vocabularies/*'`
     - taxonomy, found in `'ckanext/dataoverheid/resources/taxonomies/*'`

    Will raise a Exception under the following conditions:
     - No list is found locally with the given name
     - The local list contains content that could not be parsed as valid JSON

    :param str name: The name of the list to load
    :param str local_name: The name of the list on the filesystem
    :param str list_type: The type of list to load
    :rtype: list of str
    :return: The entries of the loaded list
    """
    types_map = {
        'vocabulary': 'vocabularies',
        'taxonomy': 'taxonomies'
    }
    special = [
        'CKAN:License',
        'Overheid:License'
    ]

    try:
        list_type = types_map.get(list_type)
        filepath = os.path.join(os.path.dirname(__file__), '..', '..',
                                'resources', list_type, local_name)

        with open(filepath, 'r') as file_contents:
            parsed = json.loads(file_contents.read())

            try:
                return [block['id'] for block in parsed] if name in special \
                    else list(parsed.keys())
            except KeyError:
                raise Exception(name + ' is malformed')
    except KeyError:
        raise Exception('the requested vocabulary ' + name + ' does not exist '
                                                             'or is not supported')


def _load_config_file():
    """
    Loads the contents from the ckanext-dataoverheid configuration file and
    stores it in Redis for later use. Additionally all the vocabularies and
    taxonomies used in DCAT-AP-DONL are stored in Redis so that they can be made
    available to CKAN during the package validation process.

    The Redis cache will be updated once every 24 hours on the first request of
    the day.

    :rtype: None
    """
    current_date = str(datetime.strftime(datetime.now(), '%Y%m%d'))
    cache_key = redis_key + '_cache_date'

    if current_date == redis_conn.get(cache_key):
        return

    filepath = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                            'config.json')

    with open(filepath, 'r') as config_file:
        config_keys = [
            'validation', 'transformations', 'dcat', 'solr',
            'properties_to_remove'
        ]
        contents = json.load(config_file)

        redis_conn.set(cache_key, current_date)

        for redis_config_key in config_keys:
            redis_conn.set(config_key + redis_config_key,
                           json.dumps(contents.get(redis_config_key)))

        [redis_conn.set(redis_key + 'vocabulary.{0}'.format(key),
                        json.dumps(_load_list(key, voc['local'], 'vocabulary')))
         for key, voc in contents.get('validation')['vocabularies'].items()]

        [redis_conn.set(redis_key + 'taxonomy.{0}'.format(key),
                        json.dumps(_load_list(key, tax['local'], 'taxonomy')))
         for key, tax in contents.get('validation')['taxonomies'].items()]


redis_key = 'ckanext.dataoverheid:'
config_key = redis_key + 'config.'
redis_conn = connect_to_redis()
_load_config_file()
