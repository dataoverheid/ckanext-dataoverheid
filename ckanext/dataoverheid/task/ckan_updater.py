# encoding: utf-8


import json
import logging
import os
import urllib2


def update_vocabulary(name, local_file, online_resource):
    """
    Updates a given vocabulary based on the contents of the online resource.

    :param str name:            The name of the vocabulary
    :param str local_file:      The local file representing the vocabulary
    :param str online_resource: The online version of the vocabulary

    :return: void
    """
    logging.info('')
    logging.info('')
    logging.info('%s', name)

    try:
        logging.info('  source            %s', online_resource)

        resource = urllib2.urlopen(online_resource)
        path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'vocabularies', str(local_file))

        logging.info('  target            %s', path)

        with open(path, 'wb') as fh:
            fh.write(resource.read())
            logging.info('  result            updated')

        if name == 'Overheid:License':
            update_vocabulary('CKAN:License', 'ckan_license.json', online_resource)
    except urllib2.HTTPError:
        logging.error('  result            failed')
        logging.error('                    resource could not be downloaded')
    except urllib2.URLError:
        logging.error('  result            failed')
        logging.error('                    source is not a valid url')
    except Exception, e:
        logging.error('  result            failed')
        logging.error('                    %s', e.message)


def update_taxonomy(name, local_file, online_resource):
    """
    Updates a given taxonomy based on the contents of the online resource.

    :param str name:            The name of the taxonomy
    :param str local_file:      The local file representing the taxonomy
    :param str online_resource: The online version of the taxonomy

    :return: void
    """
    logging.info('')
    logging.info('')
    logging.info('%s', name)

    try:
        logging.info('  source            %s', online_resource)

        taxonomy_content = {taxonomy['field_identifier']: taxonomy
                            for taxonomy in json.loads(urllib2.urlopen(online_resource).read())}
        path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'taxonomies', str(local_file))

        logging.info('  target            %s', path)

        with open(path, 'wb') as fh:
            json.dump(taxonomy_content, fh)
            logging.info('  result            updated')
    except urllib2.HTTPError:
        logging.error('  result            failed')
        logging.error('                    resource could not be downloaded')
    except urllib2.URLError:
        logging.error('  result            failed')
        logging.error('                    source is not a valid url')
    except Exception, e:
        logging.error('  result            failed')
        logging.error('                    %s', e.message)


def update_vocabularies(config):
    """
    Updates all the vocabularies defined in the given config dictionary under the 'vocabularies' key.

    :param dict config: A dictionary containing the configuration data of the ckanext-dataoverheid extension

    :return: void
    """
    [update_vocabulary(vocabulary_name, vocabulary['local'], vocabulary['online'])
     for vocabulary_name, vocabulary in config['vocabularies'].iteritems()]


def update_taxonomies(config):
    """
    Updates all the taxonomies defined in the given config dictionary under the 'taxonomies' key.

    :param dict config: A dictionary containing the configuration data of the ckanext-dataoverheid extension

    :return: void
    """
    [update_taxonomy(taxonomy_name, vocabulary['local'], vocabulary['online'])
     for taxonomy_name, vocabulary in config['taxonomies'].iteritems()]


def get_config():
    """
    Loads the ckanext-dataoverheid config.json file and returns its 'validation' key as a dictionary.

    :return: dict The configuration dictionary containing the vocabularies and taxonomies
    """
    config_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.json')

    logging.info('config source     %s', config_file)

    with open(config_file, 'r') as config_contents:
        config = json.load(config_contents)['validation']

    return config


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser(description='updates the CKAN Schema validation lists')
    parser.add_argument('--list', type=str, choices=['vocabulary', 'taxonomy'], help='which type of lists to update')
    parser.add_argument('--console', type=bool, nargs='?', const=True, default=False, help='to enable console logging')

    input_arguments = parser.parse_args()

    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), '../log/ckan_updater.log'),
                        level=logging.INFO, format='%(asctime)s \t %(levelname)s \t %(message)s')

    if input_arguments.console:
        logging.getLogger().addHandler(logging.StreamHandler())

    logging.info('')
    logging.info('')
    logging.info('ckan_updater.py')
    logging.info('')
    logging.info('input:            list:%s', input_arguments.list)

    updaters = {
        'vocabulary': update_vocabularies,
        'taxonomy': update_taxonomies
    }
    updaters[input_arguments.list](get_config())

    logging.info('')
    logging.info('')
