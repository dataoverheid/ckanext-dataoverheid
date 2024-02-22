# encoding: utf-8


from future import standard_library
standard_library.install_aliases()
from builtins import str
import json
import logging
import os
import urllib.request, urllib.error, urllib.parse


def update_vocabulary(name, local_file, online_resource):
    """
    Updates a given vocabulary based on the contents of the online resource.

    :param str name: The name of the vocabulary
    :param str local_file: The local file representing the vocabulary
    :param str online_resource: The online version of the vocabulary
    :rtype: None
    """
    logging.info('')
    logging.info('')
    logging.info('%s', name)

    try:
        logging.info('  source            %s', online_resource)

        resource = urllib.request.urlopen(online_resource)
        path = os.path.join(os.path.dirname(__file__), '..', 'resources',
                            'vocabularies', str(local_file))

        logging.info('  target            %s', path)

        with open(path, 'wb') as fh:
            fh.write(resource.read())
            logging.info('  result            updated')
    except urllib.error.HTTPError:
        logging.error('  result            failed')
        logging.error('                    resource could not be downloaded')
    except urllib.error.URLError:
        logging.error('  result            failed')
        logging.error('                    source is not a valid url')
    except Exception as e:
        logging.error('  result            failed')
        logging.error('                    %s', str(e))


def update_taxonomy(name, local_file, online_resource):
    """
    Updates a given taxonomy based on the contents of the online resource.

    :param str name: The name of the taxonomy
    :param str local_file: The local file representing the taxonomy
    :param str online_resource: The online version of the taxonomy
    :rtype: None
    """
    logging.info('')
    logging.info('')
    logging.info('%s', name)

    try:
        logging.info('  source            %s', online_resource)

        content = {taxonomy['field_identifier']: taxonomy
                   for taxonomy in json.loads(urllib.request.urlopen(online_resource).
                                              read())}
        path = os.path.join(os.path.dirname(__file__), '..', 'resources',
                            'taxonomies', str(local_file))

        logging.info('  target            %s', path)

        with open(path, 'w') as fh:
            json.dump(content, fh)
            logging.info('  result            updated')
    except urllib.error.HTTPError:
        logging.error('  result            failed')
        logging.error('                    resource could not be downloaded')
    except urllib.error.URLError:
        logging.error('  result            failed')
        logging.error('                    source is not a valid url')
    except Exception as e:
        logging.error('  result            failed')
        logging.error('                    %s', str(e))


def update_vocabularies(config):
    """
    Updates all the vocabularies defined in the given config dictionary under
    the 'vocabularies' key.

    :param dict[str, Any] config: A dictionary containing the configuration data
                                  of the ckanext-dataoverheid extension
    :rtype: None
    """
    [update_vocabulary(name, vocabulary['local'], vocabulary['online'])
     for name, vocabulary in list(config['vocabularies'].items())]


def update_taxonomies(config):
    """
    Updates all the taxonomies defined in the given config dictionary under the
    'taxonomies' key.

    :param dict[str, Any] config: A dictionary containing the configuration data
                                  of the ckanext-dataoverheid extension
    :rtype: None
    """
    [update_taxonomy(taxonomy_name, vocabulary['local'], vocabulary['online'])
     for taxonomy_name, vocabulary in list(config['taxonomies'].items())]


def get_config():
    """
    Loads the ckanext-dataoverheid config.json file and returns its 'validation'
    key as a dictionary.

    :rtype: dict[str, Any]
    :return: The configuration dictionary containing the vocabularies and
             taxonomies
    """
    config_file = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                               'config.json')

    logging.info('config source     %s', config_file)

    with open(config_file, 'r') as config_contents:
        config = json.load(config_contents)['validation']

    return config


def setup_logger(enable_console=False):
    """
    Configures the Python logger as desired.

    :param bool enable_console: To enable logging to the console
    :rtype: None
    """
    logging.basicConfig(format='%(asctime)s \t %(levelname)s \t %(message)s',
                        filename=os.path.join(os.path.dirname(__file__),
                                              '../log/ckan_updater.log'),
                        level=logging.DEBUG)

    if enable_console:
        logging.getLogger().addHandler(logging.StreamHandler())


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser(description='updates the CKAN Schema '
                                                 'validation lists')
    parser.add_argument('--list', type=str, choices=['vocabulary', 'taxonomy'],
                        help='which type of lists to update')
    parser.add_argument('--console', type=bool, nargs='?', const=True,
                        default=False, help='to enable console logging')

    input_arguments = parser.parse_args()
    setup_logger(input_arguments.console)

    logging.info('')
    logging.info('ckan_updater.py starting')
    logging.info('')
    logging.info('input:            list:%s', input_arguments.list)

    updaters = {
        'vocabulary': update_vocabularies,
        'taxonomy': update_taxonomies
    }
    updaters[input_arguments.list](get_config())

    logging.info('')
    logging.info('ckan_updater.py finished')
    logging.info('')
