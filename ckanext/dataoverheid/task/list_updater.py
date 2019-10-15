# encoding: utf-8


import os
import json
import logging
import urllib2


def update_vocabulary(name, local_file, online_resource):
    """
    Updates a given vocabulary based on the contents of the online resource.

    :param str name:            The name of the vocabulary
    :param str local_file:      The local file representing the vocabulary
    :param str online_resource: The online version of the vocabulary

    :return: void
    """
    try:
        resource = urllib2.urlopen(online_resource)
        path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'vocabularies', str(local_file))

        with open(path, 'wb') as fh:
            fh.write(resource.read())

        if name == 'Overheid:License':
            update_vocabulary('CKAN:License', 'ckan_license.json', online_resource)
    except urllib2.HTTPError:
        logging.error('%s; the online resource %s could not be reached.', name, online_resource)
    except urllib2.URLError:
        logging.error('%s; the url %s appears to be invalid.', name, online_resource)
    except Exception, e:
        logging.error('%s; unknown error %s', name, e.message)


def update_taxonomy(name, local_file, online_resource):
    """
    Updates a given taxonomy based on the contents of the online resource.

    :param str name:            The name of the taxonomy
    :param str local_file:      The local file representing the taxonomy
    :param str online_resource: The online version of the taxonomy

    :return: void
    """
    try:
        taxonomy_content = {taxonomy['field_identifier']: taxonomy
                            for taxonomy in json.loads(urllib2.urlopen(online_resource).read())}
        path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'taxonomies', str(local_file))

        with open(path, 'wb') as fh:
            json.dump(taxonomy_content, fh)
    except urllib2.HTTPError:
        logging.error('%s; the online resource %s could not be reached.', name, online_resource)
    except urllib2.URLError:
        logging.error('%s; the url %s appears to be invalid.', name, online_resource)
    except Exception, e:
        logging.error('%s; unknown error %s', name, e.message)


if __name__ == '__main__':
    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), '../log/list_updater.log'),
                        level=logging.INFO, format='%(asctime)s \t %(levelname)s \t %(message)s')

    with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.json'), 'r') as config_file:
        validation_config = json.load(config_file)['validation']

        [update_vocabulary(vocabulary_name, vocabulary['local'], vocabulary['online'])
         for vocabulary_name, vocabulary in validation_config['vocabularies'].iteritems()]

        [update_taxonomy(taxonomy_name, vocabulary['local'], vocabulary['online'])
         for taxonomy_name, vocabulary in validation_config['taxonomies'].iteritems()]
