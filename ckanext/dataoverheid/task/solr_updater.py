# encoding: utf-8


from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
import dateutil.parser as date_parser
import json
import os
import logging
import urllib.request, urllib.error, urllib.parse
import time


class SolrCore(object):
    def __init__(self, solr_host, core_name, auth=None):
        """
        Initialize a SolrCore instance.

        :param str            solr_host: The full URL to the Solr installation
        :param str            core_name: The name of the Solr core
        :param dict[str, str] auth:      A dictionary containing a 'username'
                                         and a 'password' key used to provide
                                         BasicAuth credentials to the Solr host

        :rtype: SolrCore
        """
        self.solr_host = solr_host
        self.core_name = core_name
        self.authentication = None

        if auth:
            basic_auth = auth['username'] + ':' + auth['password']
            basic_auth = 'Basic ' + basic_auth.encode('base64')

            self.authentication = basic_auth.replace('\n', '')

    def document_count(self, selector='*:*'):
        """
        Retrieve the total amount of documents that match the given selector.

        :param str selector: The 'q' parameter of a Solr query

        :rtype:  int|None
        :return: The amount of documents that match the query, or None if the
                 request failed
        """
        return self.select_documents({
            'q': selector,
            'wt': 'json',
            'rows': 0
        })['response']['numFound']

    def select_documents(self, query):
        """
        Select and return documents from the Solr index that match the given
        query.

        :param dict[str, Any] query: The Solr query to perform to identify the
                                     documents to select

        :rtype: dict[str, Any]|None
        :return: The response as a JSON dictionary, or None if the request
                 failed
        """
        response = self._execute_request(self._create_core_request('select', {
            'params': query
        }))

        if not response:
            return None

        return json.loads(response.read())

    def select_all_documents(self, fq=None, fl=None,
                             documents_per_request=1000):
        """
        Selects all the documents from the Solr core and returns them as a JSON
        object.

        :param str fq: The filter query to apply
        :param list of str fl: The fields to select per document, defaults to
                               '*'
        :param int documents_per_request: The amount of documents to  retrieve
                   per request

        :rtype: list of dict[str, Any]
        :return: The complete list of documents selected from the Solr core
        """
        document_count = self.document_count('*:*')
        selected_documents = []

        for i in range(0, document_count, documents_per_request):
            query = {
                'q': '*:*',
                'fq': fq,
                'fl': '*' if fl is None else ','.join(fl),
                'start': i,
                'rows': documents_per_request,
                'wt': 'json'
            }
            query = dict((k, v) for k, v in query.items() if v is not None)
            selected_documents.append(
                self.select_documents(query)['response']['docs']
            )

        return [document for batch in selected_documents for document in batch]

    def index_documents(self, documents, commit=True, batch_size=200):
        """
        Add the given documents to the index of the Solr core.

        :param list of dict[str, Any] documents: The list of dictionaries that
                                                 represent the documents to
                                                 index
        :param bool commit: Whether or not to commit the changes made to the
                            Solr core to the  index
        :param int batch_size: The amount of documents to send to Solr per
                               batch, defaults to 200
        :rtype:  bool
        :return: Whether or not the documents were added to the index
        """
        batches = [documents[i:i+batch_size]
                   for i in range(0, len(documents), batch_size)]

        [self._execute_request(self._create_core_request(
            'update{0}'.format('?commit=true' if commit else ''), batch))
         for batch in batches]

    def delete_documents(self, query, commit=True):
        """
        Delete all the documents from the Solr core's index that match the given
        query.

        :param str query: The Solr query to identify the documents to delete
        :param bool commit: Whether or not to write the changes to the Solr
                            index
        :rtype:  bool
        :return: Whether or not the documents that match the query were deleted
                 from the Solr core
        """
        logging.info(' deleting:        %d documents from %s',
                     self.document_count(query), self.core_name)

        return self._execute_request(self._create_core_request(
            'update{0}'.format('?commit=true' if commit else ''),
            {'delete': {'query': query}})
        ) is not None

    def reload(self):
        """
        Reloads this Solr core.

        :rtype:  bool
        :return: Whether or not the core was successfully reloaded
        """
        logging.info(' reloading:       %s', self.core_name)

        return self._execute_request(self._create_solr_request(
            'admin/cores?action=RELOAD&core={0}'.format(self.core_name)
        )) is not None

    def _create_core_request(self, request, json_data=None):
        """
        Creates a urllib2 Request object based on the given request and possible
        JSON post data.

        :param str request: The request, containing only the segments after
                            '{solr_host}/{solr_core}/'
        :param dict[str, Any]|list of str json_data: The optional JSON data to
                                                     include in the request
        :rtype:  urllib2.Request
        :return: The created urllib2 Request object
        """
        return self._create_solr_request('{0}/{1}'.format(self.core_name,
                                                          request), json_data)

    def _create_solr_request(self, request, json_data=None):
        """
        Creates a urllib2 Request object based on the given Solr host and the
        request string and possible JSON body.

        :param str request: The request, containing only the segments after
                            '{solr_host}/'
        :param dict[str, Any]|list of str json_data: The optional JSON data to
                                                     include in the request
        :rtype:  urllib2.Request
        :return: The created urllib2 Request object
        """
        req = urllib.request.Request('{0}/{1}'.format(self.solr_host, request))

        if json_data:
            req.add_header('Content-Type', 'application/json')
            req.add_data(json.dumps(json_data))

        if self.authentication:
            req.add_header('Authorization', self.authentication)

        return req

    @staticmethod
    def _execute_request(request, method=None):
        """
        Execute a request against the Solr installation. The HTTP method will be
        either GET or POST depending on the presence of data in the request. if
        'method' is provided, the given method will be used instead.

        :param urllib2.Request request: The request object to execute
        :param str method: Which HTTP method to use
        :rtype:  Any|None
        :return: The response of the request, or None if the request failed
        """
        try:
            if method:
                request.get_method = lambda: method

            return urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            logging.error('request failed;')
            logging.error(' response: urllib2.HTTPError')
            logging.error(' call:     %s', request.get_full_url())
            logging.error('           %s', e.reason)
        except urllib.error.URLError as e:
            logging.error('request failed;')
            logging.error(' call:     %s', request.get_full_url())
            logging.error(' response: urllib2.URLError')
            logging.error('           %s', e.message)

        return None


class DonlSearchCore(SolrCore):
    def __init__(self, solr_host, authentication):
        """
        Initialize a DonlSearchCore instance.

        :param str solr_host: The full URL to the Solr installation
        :param dict[str, str] authentication: A dictionary containing a
                                              'username' and a 'password' key
                                              used to provide BasicAuth
                                              credentials to the Solr host
        :rtype: DonlSearchCore
        """
        SolrCore.__init__(self, solr_host, 'donl_search', authentication)

    def select_managed_stopwords(self, name):
        """
        Retrieve all the managed stopwords for the given name from the Solr
        core.

        :param   str name: The name of the stopwords list
        :rtype:  list of str|None
        :return: The list of managed stopwords, or None if the request failed
        """
        response = self._execute_request(self._create_core_request(
            'schema/analysis/stopwords/{0}'.format(name)
        ))

        if not response:
            return None

        return json.load(response)['wordSet']['managedList']

    def add_managed_stopwords(self, name, values):
        """
        Add the given values as stopwords to the managed stopwords list with the
        given name.

        :param str name: The name of the managed list
        :param list of str values: The list of values to add
        :rtype:  bool
        :return: Whether or not the stopwords were added successfully
        """
        return self._execute_request(self._create_core_request(
            'schema/analysis/stopwords/{0}'.format(name), values)
        ) is not None

    def remove_managed_stopwords(self, name, values):
        """
        Remove the given stopwords from the managed list in Solr.

        :param str         name:   The name of the managed list
        :param list of str values: The list of stopwords to remove
        :rtype: None
        """
        [self._execute_request(self._create_core_request(
            'schema/analysis/stopwords/{0}/{1}'.format(name, value)
         ), method='DELETE') for value in values]

    def select_managed_synonyms(self, name):
        """
        Retrieve the synonyms managed by Solr under the given name.

        :param str name: The name of the managed list
        :rtype: dict[str, list of str]|None
        :return: The synonym dictionary managed by Solr containing the terms as
                 keys and their synonyms as a list of
                 strings, or None if the request failed
        """
        response = self._execute_request(self._create_core_request(
            'schema/analysis/synonyms/{0}'.format(name)
        ))

        if not response:
            return None

        return json.load(response)['synonymMappings']['managedMap']

    def add_managed_synonyms(self, name, values):
        """
        Add the given synonyms to the managed synonym list in Solr.

        :param str name: The name of the managed list
        :param dict[str, list of str] values: A list of dictionaries containing
                                              synonyms to introduce
        :rtype:  bool
        :return: Whether or not the synonyms were added to the list
        """
        return self._execute_request(self._create_core_request(
            'schema/analysis/synonyms/{0}'.format(name), values
        )) is not None

    def remove_managed_synonyms(self, name, values):
        """
        Remove the given synonyms from the managed synonyms with the given name
        in Solr.

        :param str name: The name of the managed list
        :param list values: The list of synonyms to remove
        :rtype: None
        """
        [self._execute_request(self._create_core_request(
            'schema/analysis/synonyms/{0}/{1}'.format(name, value)
         ), method='DELETE') for value in values]


class DonlSuggesterCore(SolrCore):
    def __init__(self, solr_host, authentication):
        """
        Initialize a DonlSuggesterCore instance.

        :param str solr_host: The full URL to the Solr installation
        :param dict[str, str] authentication: A dictionary containing a
                                              'username' and a 'password' key
                                              used to provide BasicAuth
                                              credentials to the Solr host
        :rtype: DonlSuggesterCore
        """
        SolrCore.__init__(self, solr_host, 'donl_suggester', authentication)

    def build_suggestions(self, handler):
        """
        Builds the suggestions for the specified suggestion handler.

        :param str handler: The name of the suggestion handler

        :rtype:  bool
        :return: Whether or not the suggestions were built
        """
        return self._execute_request(self._create_solr_request(
            '{0}?suggest.build=true'.format(handler)
        )) is not None


class DatasetMapper(object):
    def __init__(self, mappings, fields_to_add=None):
        """
        Initializes a DatasetMapper instance.

        :param dict[str, str] mappings: The source > target key mapping
        :param dict[str, Any]|None fields_to_add: Which key: value pairs to add
                                                  to the mapped datasets
        :rtype: DatasetMapper
        """
        self.mappings = mappings
        self.fields_to_add = fields_to_add

    def apply_map(self, dataset):
        """
        Applies the mapping given to this `DatasetMapper` to the given dataset.

        Executed logic:

        - All properties are mapped according to the given map
        - Keys not present in the mapping will be stripped
        - Boolean `False` values are stripped
        - Boolean `True` values are converted to strings with their keys as
          values
        - All values will be converted to lists
        - Each `self.fields_to_add` key: value pair is added to the dataset

        :param dict[str, Any] dataset: The dataset to apply the mapping to
        :rtype:  dict[str, Any]
        :return: A dictionary containing all the mapped attributes from the
                 given dataset
        """
        ignore_list = []

        for key, value in dataset.items():
            if key not in list(self.mappings.keys()):
                continue

            if isinstance(value, bool):
                if value is True:
                    dataset[key] = key
                elif value is False:
                    ignore_list.append(key)

        document = {}

        for key, value in dataset.items():
            if key not in list(self.mappings.keys()) or key in ignore_list:
                continue

            target_key = self.mappings[key]
            document[target_key] = [] if target_key not in document \
                else document[target_key]

            if isinstance(value, list):
                [document[target_key].append(single_value)
                 for single_value in value]
            else:
                document[target_key].append(value)

        if self.fields_to_add:
            for key, value in self.fields_to_add.items():
                document[key] = value

        return document


def load_file(file_location):
    """
    Opens a given file and returns its contents.

    :param str file_location: The absolute path to the file
    :rtype:  str
    :return: The contents of the file
    """
    with open(file_location, 'r') as file_contents:
        contents = file_contents.read()

    return contents


def load_file_as_json(file_location):
    """
    Opens a file, parses its contents as JSON and returns the parsed JSON.

    :param str file_location: The absolute path to the file
    :rtype:  dict[str, Any]|list of Any
    :return: The JSON contents of the file as a dict or list
    """
    contents = load_file(file_location)

    if not contents:
        contents = {}

    return json.loads(contents)


def load_config():
    """
    Loads the contents of the configuration file of the ckanext-dataoverheid
    extension and returns it as a JSON object.

    :rtype: dict[str, Any]
    :return: The JSON encoded contents of the configuration file located at the
             root of the ckanext-dataoverheid extension.
    """
    extension_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    config_contents = load_file_as_json(os.path.join(extension_root,
                                                     'config.json'))
    config_contents['authorization'] = load_file_as_json(
        os.path.join(extension_root, 'authorization.json')
    )

    logging.info('')
    logging.info('config:           %s', os.path.join(extension_root,
                                                      'config.json'))

    return config_contents


def update_stopwords_nl(core_object):
    """
    Update the given Solr core such that its managed stopwords resource with
    name 'dutch' contains the appropriate stopwords.

    :param DonlSearchCore core_object: The core containing the dutch stopwords.
    :rtype: none
    """
    logging.info('')
    logging.info('')
    logging.info('managed resource: stopwords|dutch')

    stopwords_nl = load_file_as_json(os.path.join(os.path.dirname(__file__),
                                                  '..', 'resources', 'solr',
                                                  'stopwords_nl.json'))
    current_stopwords_nl = core_object.select_managed_stopwords('dutch')

    if not current_stopwords_nl:
        logging.info(' current:         0 stopwords')
        logging.info(' adding:          %s stopwords', len(stopwords_nl))

        core_object.add_managed_stopwords('dutch', stopwords_nl)
        return

    logging.info(' current:         %s stopwords', len(current_stopwords_nl))

    stopwords_to_add = list(set(stopwords_nl).difference(current_stopwords_nl))

    logging.info(' adding:          %s stopwords', len(stopwords_to_add))

    if len(stopwords_to_add) > 0:
        core_object.add_managed_stopwords('dutch', stopwords_to_add)

    logging.info('')


def update_uri_synonyms(core_object):
    """
    Update the given Solr core such that its managed synonyms resource with name
    'url_nl' and 'uri_en' contains the appropriate synonyms.

    :param DonlSearchCore core_object: The core containing the uri_nl and uri_en
                                       synonym lists.
    :rtype: None
    """
    uri_synonyms = {
        'uri_nl': {},
        'uri_en': {}
    }

    vocabulary_dir = os.path.join(os.path.dirname(__file__), '..', 'resources',
                                  'vocabularies')
    taxonomy_dir = os.path.join(os.path.dirname(__file__), '..', 'resources',
                                'taxonomies')

    for vocabulary_file in os.listdir(vocabulary_dir):
        is_license = vocabulary_file == 'ckan_license.json'

        if vocabulary_file.endswith('.json') and not is_license:
            filepath = os.path.join(vocabulary_dir, vocabulary_file)

            if vocabulary_file == 'overheid_license.json':
                for license in load_file_as_json(filepath):
                    key = license.get('url')
                    title = license.get('title')

                    uri_synonyms['uri_nl'][key] = title
                    uri_synonyms['uri_en'][key] = title

                continue

            for uri, properties in load_file_as_json(filepath).items():
                uri_synonyms['uri_nl'][uri] = properties['labels']['nl-NL']
                uri_synonyms['uri_en'][uri] = properties['labels']['en-US']

    for taxonomy_file in os.listdir(taxonomy_dir):
        if taxonomy_file.endswith('.json'):
            filepath = os.path.join(taxonomy_dir, taxonomy_file)

            for uri, properties in load_file_as_json(filepath).items():
                uri_synonyms['uri_nl'][uri] = properties['label_nl']
                uri_synonyms['uri_en'][uri] = properties['label_en']

    for lang in ['uri_nl', 'uri_en']:
        logging.info('')
        logging.info('managed resource: synonyms|%s', lang)

        current_uri_synonyms = core_object.select_managed_synonyms(lang)

        if not current_uri_synonyms:
            logging.info(' current:         0 synonyms')
            logging.info(' adding:          %s synonyms',
                         len(uri_synonyms[lang]))

            core_object.add_managed_synonyms(lang, uri_synonyms[lang])
            continue

        logging.info(' current:         %s synonyms', len(current_uri_synonyms))

        synonyms_to_add = {key: value
                           for key, value in uri_synonyms[lang].items()
                           if key not in list(current_uri_synonyms.keys())}

        logging.info(' adding:          %s synonyms', len(synonyms_to_add))

        if len(synonyms_to_add) > 0:
            core_object.add_managed_synonyms(lang, synonyms_to_add)

    logging.info('')


def update_hierarchy_theme(core_object):
    """
    Update the hierarchy_theme Solr managed synonym resource which is part of
    the Solr core which the core_object represents.

    :param DonlSearchCore core_object: The core containing the hierarchy_theme
                                       synonym list
    :rtype: None
    """
    for hierarchy_item in ['hierarchy_theme', 'hierarchy_theme_query']:
        logging.info('')
        logging.info('')
        logging.info('managed resource: synonyms|{0}'.format(hierarchy_item))

        hierarchy_theme = load_file_as_json(
            os.path.join(os.path.dirname(__file__), '..', 'resources', 'solr',
                         '{0}.json'.format(hierarchy_item)))
        current_hierarchy_theme = core_object.select_managed_synonyms(
            hierarchy_item
        )

        if not current_hierarchy_theme:
            logging.info(' current:         0 synonyms')
            logging.info(' adding:          %s synonyms', len(hierarchy_theme))

            core_object.add_managed_synonyms(hierarchy_item, hierarchy_theme)
            return

        logging.info(' current:         %s synonyms',
                     len(current_hierarchy_theme))

        themes_to_add = {key: value
                         for key, value in hierarchy_theme.items()
                         if key not in list(current_hierarchy_theme.keys())}

        logging.info(' adding:          %s synonyms', len(themes_to_add))

        if len(themes_to_add) > 0:
            core_object.add_managed_synonyms(hierarchy_item, themes_to_add)

        logging.info('')


def update_resource(args):
    """
    Updates one of the resources [ 'stopwords_nl', 'uri_synonyms',
    'hierarchy_theme' ] based on the resource key present in the args argument.

    If the `--reload` argument is provided then the `donl_search` core will be
    reloaded after the operation.

    :param dict[str, Any] args: The input arguments sent via the commandline
    :rtype: None
    """
    logging.info('action:           %s', args['action'])
    logging.info('input:            resource:%s', input_arguments['resource'])

    config = load_config()
    search_core = DonlSearchCore(config['solr']['host'],
                                 config['authorization'])

    action_map = {
        'stopwords_nl': update_stopwords_nl,
        'uri_synonyms': update_uri_synonyms,
        'hierarchy_theme': update_hierarchy_theme
    }

    action_map[args['resource']](search_core)

    if args['reload'] and search_core.reload():
        logging.info('donl_search core reloaded')


def determine_datasets_to_update(index_type, dataset_mapping,
                                 mapped_ckan_datasets, mapped_solr_datasets):
    """
    Determines which datasets from the `donl_dataset` core are eligible for
    updating in the `donl_search` core. If `index_type` equals False all
    datasets will be updated. When `index_type` is True only the datasets for
    which the `sys_modified` field is newer than the `sys_modified` field of the
    dataset in the `donl_search` core will be updated.

    :param bool index_type: What kind of index update to run, True = delta,
                            False = full
    :param dict[str, str] dataset_mapping: The source > target key mapping
    :param dict[str, Any] mapped_ckan_datasets: The (mapped) datasets from CKAN
    :param dict[str, Any] mapped_solr_datasets: The (mapped) datasets from Solr
    :rtype:  dict[str, dict[str, Any]]
    :return: The dictionary of datasets which should be updated in the
             `donl_search` core
    """
    datasets_to_update = {}

    for key, dataset in mapped_solr_datasets.items():
        if key not in list(mapped_ckan_datasets.keys()):
            continue

        if key in list(datasets_to_update.keys()):
            continue

        ckan_dataset = mapped_ckan_datasets[key]

        if index_type is False:
            datasets_to_update[key] = ckan_dataset
            continue

        date_key = dataset_mapping['metadata_modified']

        if date_key not in list(dataset.keys()):
            datasets_to_update[key] = ckan_dataset
            continue

        if date_key not in list(ckan_dataset.keys()):
            datasets_to_update[key] = ckan_dataset
            continue

        ckan_date = date_parser.parse(ckan_dataset[date_key][0])
        solr_date = date_parser.parse(dataset[date_key])

        if ckan_date > solr_date:
            datasets_to_update[key] = ckan_dataset

    return datasets_to_update


def update_donl_search(args):
    """
    Synchronizes the donl_search Solr core with the donl_dataset Solr core such
    that all datasets present in the donl_dataset core are also indexed as
    documents in the donl_search core.

    If the `--delta` flag is provided, only the modified datasets will be
    synchronized, otherwise *all* datasets from the `donl_dataset` core will be
    updated in the `donl_search` core, regardless if changes were detected.

    :param dict[str, Any] args: The input arguments sent via the commandline
    :rtype: None
    """
    logging.info('action:           %s', args['action'])
    logging.info('input:            index:%s',
                 'delta' if args['delta'] is True else 'full')

    config = load_config()
    dataset_mapping = config['solr']['mappings']['donl_dataset_to_donl_search']

    donl_dataset_core = SolrCore(config['solr']['host'], 'donl_dataset',
                                 config['authorization'])
    donl_search_core = DonlSearchCore(config['solr']['host'],
                                      config['authorization'])

    logging.info('')

    ckan_datasets = donl_dataset_core.select_all_documents(
        fl=list(dataset_mapping.keys())
    )
    logging.info('ckan datasets:    %s', len(ckan_datasets))

    solr_datasets = donl_search_core.select_all_documents(fq='sys_type:dataset')
    logging.info('solr datasets:    %s', len(solr_datasets))

    mapper = DatasetMapper(dataset_mapping, {'sys_type': 'dataset'})
    mapped_ckan_datasets = {dataset['id']: mapper.apply_map(dataset)
                            for dataset in ckan_datasets}
    mapped_solr_datasets = {dataset['sys_id']: dataset
                            for dataset in solr_datasets}

    logging.info('')
    logging.info('datasets mapped to donl_search schema')

    datasets_to_create = {dataset_key: dataset for dataset_key, dataset
                          in mapped_ckan_datasets.items()
                          if dataset_key not in list(mapped_solr_datasets.keys())}
    datasets_to_update = determine_datasets_to_update(args['delta'],
                                                      dataset_mapping,
                                                      mapped_ckan_datasets,
                                                      mapped_solr_datasets)
    datasets_to_delete = {dataset_key: dataset for dataset_key, dataset
                          in mapped_solr_datasets.items()
                          if dataset_key not in list(mapped_ckan_datasets.keys())}

    logging.info('')
    logging.info('analysis:')
    logging.info(' new:             %s', len(datasets_to_create))
    logging.info(' update:          %s (%s)', len(datasets_to_update),
                 'delta' if args['delta'] is True else 'full')
    logging.info(' remove:          %s', len(datasets_to_delete))
    logging.info('')

    logging.info('index results:')

    donl_search_core.index_documents(list(datasets_to_create.values()), commit=False)
    logging.info(' new:             %s', len(datasets_to_create))

    donl_search_core.index_documents(list(datasets_to_update.values()), commit=False)
    logging.info(' updated:         %s', len(datasets_to_update))

    for sys_id in list(datasets_to_delete.keys()):
        donl_search_core.delete_documents('sys_id:{0}'.format(sys_id),
                                          commit=False)
    logging.info(' deleted:         %s', len(datasets_to_delete))

    logging.info('')
    logging.info('committing index changes')
    donl_search_core.index_documents([], commit=True)
    
    logging.info('')
    logging.info('donl_search core updated')


def get_dataset_title_suggestions(config):
    """
    Get title suggestions from DonlSearchCore

    :rtype: list of dict[str, any]
    """
    mappings = {
        'title': 'dataset',
        'sys_type': 'type',
        'sys_name': 'payload',
        'sys_modified': 'weight',
        'sys_created': 'weight',
        'relation_community': 'community'
    }

    dataset_mapper = DatasetMapper(mappings)
    search_core = DonlSearchCore(config['solr']['host'],
                                 config['authorization'])
    datasets = search_core.select_all_documents('sys_type:dataset',
                                                list(mappings.keys()))
    title_suggestions = []

    for dataset in datasets:
        dataset = dataset_mapper.apply_map(dataset)
        dataset['weight'] = time.mktime(
            date_parser.parse(dataset['weight'][0]).timetuple()
        ) if 'weight' in dataset else 0
        dataset['language'] = ['nl', 'en']
        title_suggestions.append(dataset)

    return title_suggestions


def get_uri_suggestions(config, uri_field, suggester_field, donl_type):
    """
    Get uri suggestions using donl_search_core and managed synonyms

    :param dict[str, Any] config: The configuration to use for selecting DONL
                                  entities
    :param str uri_field: The uri field to get suggestions from
    :param str suggester_field: The suggester field to put suggestions in
    :param str donl_type: The DONL type to get suggestions for

    :rtype: list of dict[str, any]
    :return: The list of suggestions
    """
    search_core = DonlSearchCore(config['solr']['host'],
                                 config['authorization'])
    entities = search_core.select_all_documents(
        'sys_type:{0}'.format(donl_type), [uri_field, 'facet_community']
    )
    uris = {}

    for entity in entities:
        communities = []
        if 'facet_community' in entity:
            communities = entity['facet_community']

        if uri_field in entity:
            for uri in entity[uri_field]:
                if uri in uris:
                    uris[uri]['community'].update(communities)
                    uris[uri]['count'] += 1
                else:
                    uris[uri] = {
                        'community': set(),
                        'count': 1
                    }
                    uris[uri]['community'].update(communities)

    languages = ['nl', 'en']
    suggestions = []

    for language in languages:
        synonyms = search_core.select_managed_synonyms(
            'uri_{0}'.format(language)
        )

        for uri in list(uris.keys()):
            if uri in synonyms:
                labels = synonyms[uri]

                for label in labels:
                    suggestions.append({
                        suggester_field: label,
                        'type': donl_type,
                        'payload': uri,
                        'weight': uris[uri]['count'],
                        'language': language,
                        'community': list(uris[uri]['community'])
                    })

    return suggestions


def get_organization_suggestions(config, donl_type):
    """
    Get organization suggestions for a given type

    :param dict[str, Any] config: The configuration to use for selecting DONL
                                  organizations
    :param str donl_type: The DONL type to get suggestions for
    :rtype: list of dict[str, any]
    :return: The list of organization suggestions
    """
    return get_uri_suggestions(config, 'authority', 'organization', donl_type)


def get_theme_suggestions(config, donl_type):
    """
    Get theme suggestions for a given type

    :param dict[str, Any] config: The configuration to use for selecting DONL
                                  themes
    :param str donl_type: The DONL type to get suggestions for
    :rtype: list of dict[str, any]
    :return: The list of theme suggestions
    """
    return get_uri_suggestions(config, 'theme', 'theme', donl_type)


def update_donl_suggester(args):
    logging.info('action:           %s', args['action'])
    logging.info('input:            none')

    config = load_config()
    suggester_core = DonlSuggesterCore(config['solr']['host'],
                                       config['authorization'])

    logging.info('')
    logging.info('clearing donl_suggester core')
    suggester_core.delete_documents('*:*', commit=False)
    logging.info('')

    title_suggestions = get_dataset_title_suggestions(config)
    organization_suggestions = get_organization_suggestions(config, 'dataset')
    theme_suggestions = get_theme_suggestions(config, 'dataset')

    logging.info('index results:')

    suggester_core.index_documents(title_suggestions, commit=False,
                                   batch_size=200)
    logging.info(' titles:          %s', len(title_suggestions))

    suggester_core.index_documents(organization_suggestions, commit=False,
                                   batch_size=200)
    logging.info(' organizations:   %s', len(organization_suggestions))

    suggester_core.index_documents(theme_suggestions, commit=False,
                                   batch_size=200)
    logging.info(' themes:          %s', len(theme_suggestions))

    logging.info('')
    logging.info('committing index changes')
    suggester_core.index_documents([], commit=True)
    logging.info('')

    logging.info('reloading donl_suggester core')
    suggester_core.reload()
    logging.info('')

    logging.info('')
    logging.info('donl_suggester core updated')


def update_reverse_relations(config):
    donl_search_core = DonlSearchCore(config['solr']['host'],
                                      config['authorization'])

    for field in config['solr']['relations']:
        for relation in config['solr']['relations'][field]:
            logging.info('')
            logging.info('updating reverse relations from %s to %s',
                         field, relation)

            mapping = config['solr']['relations'][field][relation]

            field_entities = donl_search_core.select_all_documents(
                'sys_type:{0}'.format(field), ['sys_id', mapping['match'],
                                               mapping['to']]
            )

            field_entities_indexed_by_uri = {}

            for field_entity in field_entities:
                field_entities_indexed_by_uri[
                    field_entity[mapping['match']]
                ] = field_entity

            relation_entities = donl_search_core.select_all_documents(
                'sys_type:{0}'.format(relation), [mapping['match'],
                                                  mapping['from']]
            )

            field_entities_to_relation_entities = {}

            for relation_entity in relation_entities:
                if mapping['from'] not in relation_entity:
                    continue

                for uri in relation_entity[mapping['from']]:
                    if uri in field_entities_indexed_by_uri:
                        if uri not in field_entities_to_relation_entities:
                            field_entities_to_relation_entities[uri] = []

                        field_entities_to_relation_entities[uri].append(
                            relation_entity[mapping['match']]
                        )

            logging.info(' found %s %ss with %ss',
                         len(list(field_entities_to_relation_entities.keys())),
                         field, relation)

            deletes = [{
                'sys_id': field_entity['sys_id'],
                'relation_group': {
                    'remove': field_entity[mapping['to']]
                }
            } for field_entity in field_entities
                if mapping['to'] in field_entity
                and field_entity[mapping['match']]
                not in iter(field_entities_to_relation_entities.keys())]

            updates = []
            for uri in field_entities_to_relation_entities:
                updates.append({
                    'sys_id': field_entities_indexed_by_uri[uri]['sys_id'],
                    'relation_group': {
                        'set': field_entities_to_relation_entities[uri]
                    }
                })

            donl_search_core.index_documents(deletes)
            donl_search_core.index_documents(updates)

            logging.info('')
            logging.info('results')
            logging.info(' deleted:         %s', len(deletes))
            logging.info(' updated:         %s', len(updates))


def update_relations(args):
    logging.info('action:           %s', args['action'])

    config = load_config()

    donl_search_core = DonlSearchCore(config['solr']['host'],
                                      config['authorization'])

    for relation_source, mapping in config['solr']['has_relations'].items():
        logging.info('')
        logging.info('relations for %s', relation_source)

        sources = donl_search_core.select_all_documents(
            fq='sys_type:{0}'.format(relation_source)
        )
        rels = donl_search_core.select_all_documents(
            fl=list(set(list(mapping.values()) + ['sys_uri', 'sys_type'])),
            fq='sys_type:{0}'.format(' OR sys_type:'.join(list(mapping.keys())))
        )

        for source in sources:
            source['related_to'] = []

        logging.info(' subjects:        %s', len(sources))
        logging.info(' relations:       %s', len(rels))

        for mapping_target, mapping_source in mapping.items():
            for source in sources:
                if mapping_target in source['related_to']:
                    continue

                for relation in rels:
                    if mapping_target != relation['sys_type']:
                        continue

                    try:
                        if isinstance(relation[mapping_source], list):
                            if source['sys_uri'] in relation[mapping_source]:
                                source['related_to'].append(mapping_target)
                        else:
                            if source['sys_uri'] == relation[mapping_source]:
                                source['related_to'].append(mapping_target)
                    except KeyError:
                        continue

                source['related_to'] = list(set(source['related_to']))

        documents_to_update = []
        [documents_to_update.append(source)
         for source in sources if len(source['related_to']) > 0]

        excluded = [
            'uri_synonym_nl', 'uri_synonym_en', 'text', 'title_autocomplete',
            'spellcheck', '_version_'
        ]

        for document in documents_to_update:
            for key in list(document.keys()):
                if key in excluded:
                    document.pop(key)
                    continue

                if key.startswith('facet_'):
                    document.pop(key)
                    continue

                if key.startswith('relation_'):
                    document.pop(key)
                    continue

        logging.info('')
        logging.info('indexing relations')

        donl_search_core.index_documents(documents_to_update)

        logging.info('')
        logging.info('results')
        logging.info(' indexed:         %s', len(documents_to_update))

    update_reverse_relations(config)


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser(description='perform operations on the '
                                                 'local Solr installation')
    subparser = parser.add_subparsers(title='action', dest='action')

    managed_resources = subparser.add_parser('update_resource',
                                             help='update a resource managed '
                                                  'by Solr')
    managed_resources.add_argument('--resource', type=str,
                                   choices=['stopwords_nl', 'uri_synonyms',
                                            'hierarchy_theme'],
                                   help='which resource to update',
                                   required=True)
    managed_resources.add_argument('--reload', type=bool, nargs='?', const=True,
                                   default=False, help='to reload the core '
                                                       'after updating the '
                                                       'resource')
    managed_resources.add_argument('--console', type=bool, nargs='?',
                                   const=True, default=False,
                                   help='to enable console logging')

    donl_search = subparser.add_parser('update_donl_search',
                                       help='update the index of the '
                                            'donl_search Solr core')
    donl_search.add_argument('--delta', type=bool, nargs='?', const=True,
                             default=False, help='only process documents for '
                                                 'which changes are detected '
                                                 'in the donl_dataset Solr '
                                                 'core')
    donl_search.add_argument('--console', type=bool, nargs='?', const=True,
                             default=False, help='to enable console logging')

    donl_search = subparser.add_parser('update_donl_suggester',
                                       help='update the index of the '
                                            'donl_suggester Solr core')
    donl_search.add_argument('--console', type=bool, nargs='?', const=True,
                             default=False, help='to enable console logging')

    donl_relations = subparser.add_parser('update_relations',
                                          help='update the relations of all '
                                               'the indexed objects')
    donl_relations.add_argument('--console', type=bool, nargs='?', const=True,
                                default=False, help='to enable console logging')

    input_arguments = vars(parser.parse_args())

    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__),
                                              '../log/solr_updater.log'),
                        level=logging.INFO,
                        format='%(asctime)s \t %(levelname)s \t %(message)s')

    if input_arguments['console']:
        logging.getLogger().addHandler(logging.StreamHandler())

    logging.info('')
    logging.info('solr_updater.py')
    logging.info('')

    actions = {
        'update_resource': update_resource,
        'update_donl_search': update_donl_search,
        'update_donl_suggester': update_donl_suggester,
        'update_relations': update_relations
    }

    actions[input_arguments['action']](input_arguments)
