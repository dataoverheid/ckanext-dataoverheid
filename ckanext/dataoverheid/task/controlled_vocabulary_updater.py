# encoding: utf-8

"""
This script retrieves the latest versions of the DCAT-AP-DONL 1.1 controlled vocabularies and updates the local cached
versions of these vocabularies.

The results of the updater are logged in the `ckanext/dataoverheid/log/controlled_vocabulary_updater.log` file
"""

import os
import sys
import json
import logging
import urllib2


sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))


logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), '../log/controlled_vocabulary_updater.log'),
    level=logging.INFO,
    format='%(asctime)s \t %(levelname)s \t %(message)s'
)


def update_vocabulary(name, local_file, online_resource):
    """
    Updates a given vocabulary based on the contents of the online resource. The results are logged.

    :param name: The name of the vocabulary
    :param local_file: The local file representing the vocabulary
    :param online_resource: The online version of the vocabulary
    :return: void
    """
    try:
        resource = urllib2.urlopen(online_resource)

        with open(_create_file_path(local_file), 'wb') as local_source:
            local_source.write(resource.read())
    except urllib2.HTTPError:
        logging.error(u'  ✘  %s; the online resource %s could not be reached.', name, online_resource)
    except urllib2.URLError:
        logging.error(u'  ✘  %s; the url %s appears to be invalid.', name, online_resource)
    except Exception, e:
        logging.error(u'  ✘  %s; unknown error %s', name, e.message)


def _create_file_path(filename):
    """
    Creates a absolute filepath to the given filename located in the directory
    `ckanext/dataoverheid/resources/controlled_vocabularies/`.

    :param filename: The file to create the path for
    :return: string, The absolute filepath
    """
    return os.path.join(
        os.path.dirname(__file__), '..', 'resources', 'controlled_vocabularies', '' + filename
    )


if __name__ == '__main__':
    filepath = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.json')

    with open(filepath, 'r') as config_file:
        controlled_vocabularies = json.load(config_file)['controlled_vocabularies']

    for vocabulary in controlled_vocabularies:
        update_vocabulary(vocabulary['name'], vocabulary['local'], vocabulary['online'])
