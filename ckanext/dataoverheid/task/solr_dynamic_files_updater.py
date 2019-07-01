# encoding: utf-8

"""
This script generates suggestion txt files and instructs Solr to re-build the suggester if changes were detected in the
txt files.
"""


import os
import sys
import json
import logging
import urllib2


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), '../log/solr_dynamic_files_updater.log'),
    level=logging.INFO,
    format='%(asctime)s \t %(levelname)s \t %(message)s'
)


def load_file(file_location):
    """
    Opens a given file and returns its contents.

    :param file_location: str, The absolute path to the file
    :return: str, the contents of the file
    """
    with open(file_location, 'a+') as file_contents:
        contents = file_contents.read()

    return contents


def load_file_as_json(file_location):
    """
    Opens a file, parses its contents as JSON and returns the parsed JSON.

    :param file_location: str, The absolute path to the file
    :return: The JSON contents of the file as a dict or list
    """
    contents = load_file(file_location)

    if not contents:
        contents = {}

    return json.loads(contents)


def write_to_file(file_location, file_contents):
    """
    Writes the given contents to the given file.

    :param file_location: The file to write to
    :param file_contents: The contents to write
    :return: void
    """
    with open(file_location, 'wb') as target_file:
        target_file.write(file_contents)


def build_suggestions(url):
    """
    Builds suggestions by calling the given url.

    :param url: The url which will instruct Solr to build suggestions
    :return: void
    """
    try:
        urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        logging.error(u'Failed to build suggestions;')
        logging.error(u'  Response: HTTPError')
        logging.error(u'            %s', e.reason)
    except urllib2.URLError, e:
        logging.error(u'Failed to build suggestions;')
        logging.error(u'  Call:     %s', url)
        logging.error(u'  Response: URLError')
        logging.error(u'            %s', e.reason)


if '__main__' == __name__:
    logging.info(u'Starting solr_dynamic_files_updater.py;')

    extension_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    configuration = load_file_as_json(os.path.join(extension_root, 'config.json'))
    donl_organizations = load_file_as_json(os.path.join(extension_root, configuration['solr_donl_organization_file']))

    suggestion_pattern = u'{0}\t0.0\t{1}'

    organizations_nl = []
    organizations_en = []

    for identifier, data in donl_organizations.items():
        organizations_nl.append(suggestion_pattern.format(data['labels']['nl-NL'], identifier))
        organizations_en.append(suggestion_pattern.format(data['labels']['en-US'], identifier))

    target_directories = configuration['solr_dynamic_files_target_directories']

    organizations_nl_as_txt = '\n'.join(organizations_nl)
    organizations_en_as_txt = '\n'.join(organizations_en)

    for directory in target_directories:
        current_nl_suggestions_file_path = os.path.join(extension_root, directory, 'authority_suggestions_nl.txt')
        current_nl_suggestions = load_file(current_nl_suggestions_file_path)

        current_en_suggestions_file_path = os.path.join(extension_root, directory, 'authority_suggestions_en.txt')
        current_en_suggestions = load_file(current_en_suggestions_file_path)

        if organizations_nl_as_txt != current_nl_suggestions:
            write_to_file(current_nl_suggestions_file_path, organizations_nl_as_txt)

            logging.info(u'Changes detected in {0}{1};'.format(directory, u'authority_suggestions_nl.txt'))

        if organizations_en_as_txt != current_en_suggestions:
            write_to_file(current_en_suggestions_file_path, organizations_en_as_txt)

            logging.info(u'Changes detected in {0}{1};'.format(directory, u'authority_suggestions_en.txt'))

    logging.info(u'Rebuilding suggestion index;')
    build_suggestions(configuration['solr_suggestions_build_url'])
