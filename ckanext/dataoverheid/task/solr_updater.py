# encoding: utf-8


import os
import json
import logging
import urllib
import urllib2
import time
import dateutil.parser as parser


def load_file(file_location):
    """
    Opens a given file and returns its contents.

    :param str file_location: The absolute path to the file

    :return: str, The contents of the file
    """
    with open(file_location, 'a+') as file_contents:
        contents = file_contents.read()

    return contents


def load_file_as_json(file_location):
    """
    Opens a file, parses its contents as JSON and returns the parsed JSON.

    :param str file_location: The absolute path to the file

    :return: dict|list The JSON contents of the file as a dict or list
    """
    contents = load_file(file_location)

    if not contents:
        contents = {}

    return json.loads(contents)


def build_suggestions(url, authorization):
    """
    Builds suggestions by calling the given url.

    :param str url:            The url which will instruct Solr to build suggestions
    :param dict authorization: The credentials for Solr

    :return: void
    """
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Basic {0}'.format('{0}:{1}'.format(authorization['username'],
                                                                        authorization['password'])
                                                       .encode('base64')).replace('\n', ''))

    try:
        urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logging.error('Failed to build suggestions;')
        logging.error('  Response: HTTPError')
        logging.error('            %s', e.reason)
    except urllib2.URLError, e:
        logging.error('Failed to build suggestions;')
        logging.error('  Call:     %s', url)
        logging.error('  Response: URLError')
        logging.error('            %s', e.reason)


def reload_core(url, authorization):
    """
    Reloads core by calling the given url.

    :param str url:            The url which will instruct Solr to reload core
    :param dict authorization: The credentials for Solr

    :return: void
    """
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Basic {0}'.format('{0}:{1}'.format(authorization['username'],
                                                                        authorization['password'])
                                                       .encode('base64')).replace('\n', ''))

    try:
        urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logging.error('Failed to reload core;')
        logging.error('  Response: HTTPError')
        logging.error('            %s', e.reason)
    except urllib2.URLError, e:
        logging.error('Failed to reload core;')
        logging.error('  Call:     %s', url)
        logging.error('  Response: URLError')
        logging.error('            %s', e.reason)


def select_docs(url, params, authorization):
    """
    Gets Solr json response from Solr url

    :param str url:            The Solr url to request
    :param dict params:        Additional url parameters
    :param dict authorization: The credentials for Solr

    :return: dict, The JSON decoded Solr response
    """
    req = urllib2.Request('{0}?{1}'.format(url, urllib.urlencode(params)))
    req.add_header('Authorization', 'Basic {0}'.format('{0}:{1}'.format(authorization['username'],
                                                                        authorization['password'])
                                                       .encode('base64')).replace('\n', ''))

    try:
        response = urllib2.urlopen(req)

        return json.loads(response.read())
    except urllib2.HTTPError, e:
        logging.error('Failed to select documents;')
        logging.error('  Response: HTTPError')
        logging.error('            %s', e.reason)
    except urllib2.URLError, e:
        logging.error('Failed to select documents;')
        logging.error('  Call:     %s', url)
        logging.error('  Response: URLError')
        logging.error('            %s', e.reason)


def delete_by_query(query, url, authorization):
    """
    Sends JSON encoded delete query to Solr url

    :param str query:          Solr query string
    :param str url:            The Solr url for deletion
    :param dict authorization: The credentials for Solr

    :return: void
    """
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Basic {0}'.format('{0}:{1}'.format(authorization['username'],
                                                                        authorization['password'])
                                                       .encode('base64')).replace('\n', ''))
    req.add_data(json.dumps({'delete': {'query': query}}))

    try:
        urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logging.error('Failed to delete documents by query;')
        logging.error('  Response: HTTPError')
        logging.error('            %s', e.reason)
    except urllib2.URLError, e:
        logging.error('Failed to delete documents by query;')
        logging.error('  Call:     %s', url)
        logging.error('  Response: URLError')
        logging.error('            %s', e.reason)


def index_suggestions(url, suggestions, authorization):
    """
    Indexes suggestion to Solr url

    :param str url:            The Solr url for indexing
    :param list suggestions:   A list of key value objects
    :param dict authorization: The credentials for Solr

    :return: void
    """
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Basic {0}'.format('{0}:{1}'.format(authorization['username'],
                                                                        authorization['password'])
                                                       .encode('base64')).replace('\n', ''))
    req.add_data(json.dumps(suggestions))

    try:
        urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logging.error('Failed to index suggestions;')
        logging.error('  Response: HTTPError')
        logging.error('            %s', e.reason)
    except urllib2.URLError, e:
        logging.error('Failed to index suggestions;')
        logging.error('  Call:     %s', url)
        logging.error('  Response: URLError')
        logging.error('            %s', e.reason)


def write_uri_to_label_synonym_file(config, out_dir, out_file, language):
    """
    Write a given list of vocabularies to a Solr synonym file: URI => label.

    :param dict config:  A dict of JSON vocabularies
    :param str out_dir:  Directory in which the synonym file is written
    :param str out_file: Name of the new file
    :param str language: language code, e.g. 'nl-NL', 'en-US'

    :return: void
    """
    with open(os.path.join(out_dir, out_file), 'w') as fp:
        uris_to_label = []

        for vocabulary in config['vocabularies']:
            vocabulary_json = load_file_as_json(os.path.join(extension_root, config['vocabulary_base_path'],
                                                             config['vocabularies'][vocabulary]['local']))
            if vocabulary == 'Overheid:License':
                uris_to_label += ['{0} => {1}'.format(license['url'].encode('UTF-8'), license['title'].encode('UTF-8'))
                                  for license in vocabulary_json]
            else:
                uris_to_label += ['{0} => {1}'.format(uri.encode('UTF-8'),
                                                      vocabulary_json[uri]['labels'][language].encode('UTF-8'))
                                  for uri in vocabulary_json]

        fp.write('\n'.join(uris_to_label))


def index_facet_suggestions(facet, vocabulary_content, config, field, community=None):
    """
    Fills the ckan_suggester core with documents containing the amount of datasets per uri in a given facet.

    :param list facet:              The facets to insert as documents into the ckan_suggester core
    :param dict vocabulary_content: The human readable version of the uris contained in the facet
    :param dict config:             Contains the current configuration settings
    :param str field:               The field in the suggester core the suggestions are indexed to
    :param str community:           Community to which the facet corresponds

    :return: void
    """
    suggestions = []

    for uri in vocabulary_content:
        try:
            count = facet[facet.index(uri) + 1]
        except ValueError:
            count = 0

        suggestions.append({
            'id': uri,
            '{0}_nl'.format(field): vocabulary_content[uri]['labels']['nl-NL'],
            '{0}_en'.format(field): vocabulary_content[uri]['labels']['en-US'],
            'payload': uri,
            'weight': count,
            'community': community
        })

    index_suggestions('{0}/{1}/{2}'.format(config['solr']['host'], config['solr']['cores']['suggester']['name'],
                                           config['solr']['actions']['update'], config['solr']['authorization']),
                      suggestions, config['solr']['authorization'])


def get_document_count(config):
    """
    Retrieves the accurate total document count by performing a wildcard query against Solr.

    :param dict config: The configuration pertaining to Solr

    :return: int, The total amount of documents
    """
    query = {
        'q': '*:*',
        'wt': 'json',
        'rows': 0
    }

    return select_docs('{0}/{1}/select'.format(config['host'], config['cores']['dataset']['name']),
                       query, config['authorization'])['response']['numFound']


def get_all_documents(config, document_count):
    """
    Retrieve all the `x` documents from Solr.

    :param dict config:        The configuration pertaining to Solr
    :param int document_count: The amount of documents to request

    :return: dict, All the resulting documents
    """
    query = {
        'q': '*:*',
        'fl': 'title,name,metadata_modified,metadata_created,communities',
        'wt': 'json',
        'rows': document_count
    }

    return select_docs('{0}/{1}/select'.format(config['host'], config['cores']['dataset']['name']), query,
                       config['authorization'])


def clear_ckan_suggester_core(config):
    """
    Empties the Suggester core.

    :param dict config: The configuration pertaining to Solr

    :return: void
    """
    delete_by_query('*:*', '{0}/{1}/{2}'.format(config['host'], config['cores']['suggester']['name'],
                                                config['actions']['update']), config['authorization'])


def fill_ckan_suggester_core(ext_root, config):
    """
    Generates suggestions based on title, theme and authority.

    :param str ext_root: The root of the `ckanext-dataoverheid` extension
    :param dict config:  The configuration pertaining to Solr

    :return: void
    """
    solr_config = config['solr']
    communities = []
    facet_communities = select_docs('{0}/{1}/select'.format(solr_config['host'],
                                                            solr_config['cores']['dataset']['name']),
                                    {
                                        'q': '*:*',
                                        'wt': 'json',
                                        'rows': 0
                                    },
                                    solr_config['authorization'])['facet_counts']['facet_fields']['facet_communities']

    [communities.append(facet_communities[i]) for i in range(0, len(facet_communities)) if i % 2 == 0]

    for vocabulary in config['validation']['vocabularies']:
        if vocabulary not in solr_config['cores']['suggester']['vocabularies']:
            continue

        facet_id = solr_config['cores']['suggester']['vocabularies'][vocabulary]['facet']
        vocabulary_contents = load_file_as_json(os.path.join(ext_root, config['validation']['vocabulary_base_path'],
                                                             config['validation']['vocabularies'][vocabulary]['local']))

        docs = select_docs('{0}/{1}/select'.format(solr_config['host'], solr_config['cores']['dataset']['name']),
                           {
                               'q': '*:*',
                               'wt': 'json',
                               'rows': 0
                           }, solr_config['authorization'])

        vocabulary_facet_count = docs['facet_counts']['facet_fields'][facet_id]

        index_facet_suggestions(vocabulary_facet_count, vocabulary_contents, config,
                                solr_config['cores']['suggester']['vocabularies'][vocabulary]['suggester_field'])

        for community in communities:
            community_docs = select_docs('{0}/{1}/select'.format(solr_config['host'],
                                                                 solr_config['cores']['dataset']['name']),
                                         {
                                             'q': '*:*',
                                             'fq': 'facet_communities:({0})'.format(community),
                                             'wt': 'json',
                                             'rows': 0
                                         }, solr_config['authorization'])

            vocabulary_facet_count = community_docs['facet_counts']['facet_fields'][facet_id]

            index_facet_suggestions(vocabulary_facet_count, vocabulary_contents, config,
                                    solr_config['cores']['suggester']['vocabularies'][vocabulary]['suggester_field'],
                                    community)

    donl_docs = get_all_documents(config['solr'], get_document_count(solr_config))
    title_suggestions = []

    for doc in donl_docs['response']['docs']:
        weight = time.mktime(parser.parse(doc['metadata_modified']).timetuple()) \
            if doc['metadata_modified'] else time.mktime(parser.parse(doc['metadata_created']).timetuple())

        if 'communities' in doc:
            title_suggestions.append({
                'id': doc['name'],
                'title': doc['title'],
                'payload': doc['name'],
                'weight': weight,
                'communities': doc['communities']
            })

        title_suggestions.append({
            'id': doc['name'],
            'title': doc['title'],
            'payload': doc['name'],
            'weight': weight,
        })

    index_suggestions('{0}/{1}/{2}'.format(solr_config['host'], solr_config['cores']['suggester']['name'],
                                           solr_config['actions']['update'], solr_config['authorization']),
                      title_suggestions, solr_config['authorization'])
    build_suggestions('{0}/{1}/{2}'.format(solr_config['host'], solr_config['cores']['suggester']['name'],
                                           solr_config['actions']['build_suggestions']), solr_config['authorization'])


def generate_uri_synonyms(ext_root, config):
    """
    Generates synonyms for the URIs in the index based on their labels.

    :param str ext_root: The root of the `ckanext-dataoverheid` extension
    :param dict config:  The configuration of the `ckanext-dataoverheid` extension

    :return: void
    """
    solr_lang_dir = os.path.join(ext_root, config['solr']['cores']['dataset']['conf'], 'lang')

    write_uri_to_label_synonym_file(config['validation'], solr_lang_dir, 'synonyms_uri_nl.txt', 'nl-NL')
    write_uri_to_label_synonym_file(config['validation'], solr_lang_dir, 'synonyms_uri_en.txt', 'en-US')

    reload_core('{0}/{1}&core={2}'.format(config['solr']['host'], config['solr']['actions']['reload'],
                                          config['solr']['cores']['dataset']['name']), config['solr']['authorization'])


if __name__ == '__main__':
    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), '../log/solr_updater.log'),
                        level=logging.INFO, format='%(asctime)s \t %(levelname)s \t %(message)s')

    extension_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    configuration = load_file_as_json(os.path.join(extension_root, 'config.json'))

    configuration['solr']['authorization'] = load_file_as_json(configuration['solr']['authorization_file'])

    clear_ckan_suggester_core(configuration['solr'])
    fill_ckan_suggester_core(extension_root, configuration)
    generate_uri_synonyms(extension_root, configuration)
