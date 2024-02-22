# encoding: utf-8


from builtins import str
from builtins import object
from ckanext.dataoverheid.logic.helpers import config
from rdflib import Graph, Literal, URIRef, Namespace, BNode
from rdflib.namespace import NamespaceManager


dcat_config = config.get_config('dcat')


class DCATGraphBuilder(object):
    """
    Enables the modelling of a DCAT-AP-DONL class as valid RDF.

    All namespaces which are part of DCAT-AP-DONL are automatically registered
    and are accessible via a dictionary at `self.ns`, where the dictionary keys
    are the namespace prefixes and their values are the actual Namespaces.
    """
    def __init__(self):
        """
        Initializes the Graph on which to build the DCAT-AP-DONL class and
        registers all namespaces and mappings.
        """
        self.graph = Graph()
        self._configure_namespaces()
        self.dcat_vocabularies = URIRef(dcat_config['vocabularies'])
        self.language_map = dcat_config['language_map']
        self.dcat_spec = dcat_config['rdf']
        self.exclusion = self.dcat_spec['_exclusions']

    def _configure_namespaces(self):
        """
        Loads all the registered namespaces from the configuration file at
        `./config.json` and registers the namespaces and their prefixes in the
        Graph.

        :rtype: None
        """
        self.ns = {}
        namespaces = dcat_config['namespaces']

        for prefix, namespace in namespaces.items():
            self.ns[prefix] = Namespace(namespace)

        ns_manager = NamespaceManager(self.graph)
        [ns_manager.bind(prefix.lower(), namespace, override=True)
         for prefix, namespace in self.ns.items()]
        self.graph.namespace_manager = ns_manager

    def add_triple(self, subject, predicate, obj):
        """
        Adds a triple to the Graph.

        :param Any subject:   The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param Any obj:       The Node value of the triple
        :rtype: None
        """
        self.graph.add((subject, predicate, obj))

    def add_literal(self, subject, predicate, literal, language_uri=None):
        """
        Adds a RDF Literal to the Graph with a given language tag, if provided.
        If no language is provided, the tag will be omitted.

        See also: `DCATGraphBuilder.add_triple()`.

        :param Any subject: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param Any literal: A list of strings or a string to act as the Node
                            value of the triple
        :param Any language_uri: The DCAT-AP-DONL language URI that specifies
                                 which language this Node value holds
        :rtype: None
        """
        if isinstance(literal, list):
            [self.add_literal(subject, predicate, literal_entry, language_uri)
             for literal_entry in literal]
            return

        if language_uri:
            self.add_triple(subject, predicate,
                            Literal(literal, self.language_map[language_uri]))
        else:
            self.add_triple(subject, predicate, Literal(literal))

    def add_number_literal(self, subject, predicate, number):
        """
        Adds a RDF literal with the XSD.decimal tag to denote its value as a
        number to the Graph.

        See also: `DCATGraphBuilder.add_triple()`.

        :param Any subject: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param Any number: A list of numbers or a number to act as the Node
                           value of the triple
        :rtype: None
        """
        if isinstance(number, list):
            [self.add_number_literal(subject, predicate, num) for num in number]
            return

        self.add_triple(subject, predicate,
                        Literal(number, datatype=self.ns['XSD'].decimal))

    def add_datetime_literal(self, subject, predicate, datetime):
        """
        Adds a RDF literal with the XSD.datetime tag to denote its value as a
        datetime to the Graph.

        See also: `DCATGraphBuilder.add_triple()`.

        :param Any subject: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param Any datetime: A list of datetimes or a datetime to act as the
                             Node value of the triple
        :rtype: None
        """
        if isinstance(datetime, list):
            [self.add_datetime_literal(subject, predicate, datetime_entry)
             for datetime_entry in datetime]
            return

        self.add_triple(subject, predicate,
                        Literal(datetime, datatype=self.ns['XSD'].datetime))

    def add_uri(self, subject, predicate, uri, vocabulary=None):
        """
        Adds a RDF Resource to the Graph. If a vocabulary is given this RDF
        Resource will be given a RDF.type triple to indicate the type of
        Resource. As all DCAT-AP-DONL Resources are defined in
        `https://data.overheid.nl/vocabularies.rdf` an additional
        RDFS.isDefinedBy triple will be added to the Resource as well to
        indicate where the definition of the Resource can be found.

        See also: `DCATGraphBuilder.add_triple()`.

        :param Any subject: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param Any uri: A list of URIs or a URI to act the Node value of the
                        triple
        :param Any vocabulary: The namespaced Class which this Resource
                               represents
        :rtype: None
        """
        if isinstance(uri, list):
            [self.add_uri(subject, predicate, uri_entry, vocabulary)
             for uri_entry in uri]
            return

        uri = URIRef(uri)

        if vocabulary:
            self.add_triple(uri, self.ns['RDFS'].isDefinedBy,
                            self.dcat_vocabularies)
            self.add_triple(uri, self.ns['RDF'].type, vocabulary)

        self.add_triple(subject, predicate, uri)

    def as_xml(self):
        """
        Outputs the current Graph in XML/RDF format.

        See also: `DCATGraphBuilder._as()`.

        :rtype: str
        :return: The XML/RDF representation of the Graph
        """
        return self.as_('xml')

    def as_n3(self):
        """
        Outputs the current Graph in text/n3 format.

        See also: `DCATGraphBuilder._as()`.

        :rtype: str
        :return: The text/n3 representation of the Graph
        """
        return self.as_('n3')

    def as_(self, output):
        """
        Attempts to output the current Graph in the given output style.

        :param str output: The output format of the Graph
        :rtype: str
        :return: The serialized Graph in the given format
        """
        return self.graph.serialize(format=output)

    def _process_class(self, target, spec, package, parent=None,
                       allow_empty=False):
        """
        Processes one of the DCAT-AP-DONL classes and add it to the Graph.

        :param Any target: The Node which acts as the subject of triples
        :param dict[Any, Any] spec: The specification for translating CKAN to
                                    DCAT
        :param dict[Any, Any] package: The complete CKAN package to model
        :param Any parent: The parent node to add the created Node to
        :param bool allow_empty: Whether or not to allow the created Node to be
                                 empty
        :rtype: None
        """
        has_properties = any((prop in package for prop in list(spec.keys())))
        class_spec = spec['class']

        if not allow_empty and not has_properties:
            return

        self.add_triple(target, self.ns['RDF'].type,
                        self.ns[class_spec['namespace']][class_spec['name']])

        for ckan_property, rdf_details in spec.items():
            if ckan_property in self.exclusion:
                continue

            current_type = rdf_details['type']
            prop = rdf_details['property']
            ns = rdf_details['namespace']

            if current_type == 'literal':
                prefix = rdf_details['prefix']

                self._add_literal_to(target, self.ns[ns][prop], prefix,
                                     ckan_property, package,
                                     package['metadata_language'])
            elif current_type == 'number':
                self._add_number_literal_to(target, self.ns[ns][prop],
                                            ckan_property, package,)
            elif current_type == 'datetime':
                prefix = rdf_details['prefix']

                self._add_datetime_literal_to(target, self.ns[ns][prop],
                                              prefix, ckan_property, package)
            elif current_type == 'uri':
                prefix = rdf_details['prefix']

                self._add_uri_to(target, self.ns[ns][prop], prefix,
                                 ckan_property, package)
            elif current_type == 'resource':
                classname = rdf_details['class']
                prefix = rdf_details['prefix']

                vocabulary = self.ns[classname['namespace']][classname['name']]

                self._add_uri_to(target, self.ns[ns][prop], prefix,
                                 ckan_property, package, vocabulary)
            elif current_type == 'boolean':
                classname = rdf_details['class']

                self._add_boolean_to(target, self.ns[ns][prop], ckan_property,
                                     package, classname['namespace'],
                                     classname['name'])

        if parent:
            self.add_triple(parent,
                            self.ns[spec['namespace']][spec['property']],
                            target)

    def _add_literal_to(self, target, predicate, prefix, prop, package,
                        language=None):
        """
        Adds a Literal node to the given target Node.

        :param Any target: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param str prefix: The prefix to prepend to the value
        :param Any prop: The property holding the value of the Literal
        :param dict[str, Any] package:  The CKAN package
        :param Any language: The language of the Literal
        :rtype: None
        """
        try:
            value = package[prop]

            if value is None:
                return

            if isinstance(value, list):
                self.add_literal(target, predicate,
                                 [prefix + val['display_name']
                                  if isinstance(val, dict) else
                                  prefix + val for val in value], language)
                return

            self.add_literal(target, predicate, (prefix + value['display_name']
                                                 if isinstance(value, dict)
                                                 else prefix + value), language)
        except KeyError:
            return

    def _add_number_literal_to(self, target, predicate, prop, package):
        """
        Adds a Literal node with the XSD.Decimal type to the given target Node.

        :param Any target: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param Any prop: The property holding the value of the Literal
        :param dict[str, Any] package: The CKAN package
        :rtype: None
        """
        try:
            value = package[prop]

            if value is None:
                return

            if isinstance(value, list):
                self.add_number_literal(target, predicate,
                                        [str(val['display_name'])
                                         if isinstance(val, dict)
                                         else str(val) for val in value])
                return

            self.add_number_literal(target, predicate, str(value))
        except KeyError:
            return

    def _add_datetime_literal_to(self, target, predicate, prefix, prop,
                                 package):
        """
        Adds a Literal node with the XSD.DateTime type to the given target Node.

        :param Any target: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param str prefix: The prefix to prepend to the value
        :param Any prop: The property holding the value of the Literal
        :param dict[str, Any] package: The CKAN package
        :rtype: None
        """
        try:
            value = package[prop]

            if value is None:
                return

            if isinstance(value, list):
                self.add_datetime_literal(target, predicate,
                                          [prefix + val['display_name']
                                           if isinstance(val, dict)
                                           else prefix + val for val in value])
                return

            self.add_datetime_literal(target, predicate, prefix + value)
        except KeyError:
            return

    def _add_uri_to(self, target, predicate, prefix, prop, package,
                    vocabulary=None):
        """
        Adds a RDF Resource to the Graph.

        :param Any target: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param str prefix: The value to prefix
        :param Any prop: The property in the CKAN package holding the value to
                         add
        :param dict[str, Any] package: The CKAN package
        :param Any vocabulary: The vocabulary of the node to add
        :rtype: void
        """
        try:
            value = package[prop]

            if value is None:
                return

            if isinstance(value, list):
                self.add_uri(target, predicate,
                             [prefix + val['display_name']
                              if isinstance(val, dict) else prefix + val
                              for val in value], vocabulary)
                return

            self.add_uri(target, predicate, prefix + value, vocabulary)
        except KeyError:
            return

    def _add_boolean_to(self, target, predicate, prop, package, class_ns,
                        class_name):
        """
        Adds a node to the target node which represents a boolean.

        :param Any target: The Node target of the triple
        :param Any predicate: The namespaced verb of the triple
        :param Any prop: The property holding the value
        :param dict[str, Any] package: The CKAN package
        :param str class_ns: The namespace prefix
        :param str class_name: The name of the class
        :rtype: None
        """
        is_string_bool = package[prop] == u'true' or package[prop] == u'True'

        try:
            if is_string_bool or package[prop] is True:
                self.add_triple(target, predicate,
                                self.ns[class_ns][class_name])
        except KeyError:
            return


class DatasetDCATGraphBuilder(DCATGraphBuilder):
    """
    Enables the modelling of a CKAN package into a valid DCAT-AP-DONL RDF model.
    """
    def __init__(self, dataset_name):
        """
        Initializes the Graph and prepares it for modelling a DCAT-AP-DONL
        Dataset.

        :param str dataset_name: The name of the dataset being modelled
        """
        DCATGraphBuilder.__init__(self)
        self.dataset = URIRef(
            dcat_config['templates']['identifier'].format(dataset_name)
        )

    def parse_ckan_package(self, package):
        """
        Parses a given CKAN package dictionary and transforms it into a valid
        set of triples which together represent the CKAN package as a
        DCAT-AP-DONL Dataset.

        The transformation is based on the spec defined in the `./config.json`
        file.

        :param dict[str, Any] package: The complete CKAN package to model
        :rtype: None
        """
        dataset_spec = self.dcat_spec['dataset']
        spec_class = dataset_spec['class']
        identifier_template = dcat_config['templates']['identifier']

        self.add_triple(self.dataset, self.ns['RDF'].type,
                        self.ns[spec_class['namespace']][spec_class['name']])
        self.add_uri(self.dataset, self.ns['RDFS'].isDefinedBy,
                     identifier_template.format(package['name']))
        self.add_uri(self.dataset, self.ns['RDFS'].isDefinedBy,
                     identifier_template.format(package['id']))

        self._process_class(self.dataset, dataset_spec, package)
        self._add_catalog_record_to_graph(package)

        for entity in ['contactPoint', 'temporal', 'legalBases']:
            node_id = 'dataset.' + package['name'] + '.' + entity

            self._process_class(BNode(node_id), self.dcat_spec[entity],
                                package, parent=self.dataset, allow_empty=False)

        for idx, resource in enumerate(package['resources']):
            self._parse_ckan_resource(self.dataset, package, idx)

        self._add_fallback_alternate_identifiers(package['id'], package['name'])

    def _add_catalog_record_to_graph(self, package):
        """
        Creates a CatalogRecord from the given CKAN package and adds it to the
        Graph. The mapping from CKAN package to DCAT CatalogRecord is found in
        `DatasetDCATGraphBuilder.dcat_spec['catalogRecord']`.

        Note: The CatalogRecord is identified by the `id` of a CKAN package, a
        Dataset is identified by its `name`. This ensures that both the
        CatalogRecord and the Dataset can be uniquely identified and referenced.

        See also: `DatasetDCATGraphBuilder._process_class()`.

        :param dict[str, Any] package: The complete CKAN package to model
        :rtype: None
        """
        templates = dcat_config['templates']
        catalog_record = URIRef(templates['identifier'].format(package['id']))

        self.add_uri(catalog_record, self.ns['RDFS'].isDefinedBy,
                     templates['dataset_definition'].format(package['name']))
        self.add_uri(catalog_record, self.ns['RDFS'].isDefinedBy,
                     templates['dataset_definition'].format(package['id']))
        self.add_triple(catalog_record, self.ns['FOAF'].primaryTopic,
                        self.dataset)
        self._process_class(catalog_record, self.dcat_spec['catalogRecord'],
                            package, parent=None, allow_empty=False)

    def _add_fallback_alternate_identifiers(self, package_id, package_name):
        """
        Adds any undeclared standard alternate identifiers used by
        data.overheid.nl.

        :param str package_id: The internal id of the CKAN package
        :param str package_name: The name of the CKAN package
        :rtype: None
        """
        donl = self.ns['DONL']

        for identifier in dcat_config['templates']['alternate_identifiers']:
            tup = (self.dataset, donl.identifier, identifier.format(package_id))

            if tup not in self.graph:
                self.add_uri(self.dataset, self.ns['ADMS'].identifier,
                             identifier.format(package_id))

            tup = (self.dataset, donl.identifier,
                   identifier.format(package_name))

            if tup not in self.graph:
                self.add_uri(self.dataset, self.ns['ADMS'].identifier,
                             identifier.format(package_name))

    def _parse_ckan_resource(self, target, package, resource_index):
        """
        Constructs a DCAT Distribution from a CKAN package.

        :param Any target: The dataset to add the resource to in the Graph
        :param dict[str, Any] package: The package being modelled
        :param int resource_index: The position of the resource in the package
        :rtype: None
        """
        dataset_def = dcat_config['templates']['dataset_definition']
        distribution = BNode('dataset.' + package['name'] + '.distribution.' +
                             str(resource_index + 1))

        self.add_uri(distribution, self.ns['RDFS'].isDefinedBy,
                     dataset_def.format(package['name']))
        self.add_uri(distribution, self.ns['RDFS'].isDefinedBy,
                     dataset_def.format(package['id']))
        self._process_class(BNode('dataset.' + package['name'] +
                                  '.distribution.' + str(resource_index + 1) +
                                  '.checksum'),
                            self.dcat_spec['checksum'],
                            package['resources'][resource_index],
                            parent=distribution, allow_empty=False)
        self._process_class(distribution, self.dcat_spec['distribution'],
                            package['resources'][resource_index], parent=target,
                            allow_empty=False)


class CatalogDCATGraphBuilder(DCATGraphBuilder):
    """
    Enables the modelling of an entire catalog as a DCAT Catalog.
    """
    def __init__(self):
        """
        Processes the DCAT Catalog class and adds it to the new Graph.
        """
        DCATGraphBuilder.__init__(self)
        self.catalog_config = dcat_config['catalog_data']
        self.catalog = URIRef(self.catalog_config['identifier'])

        spec = self.dcat_spec['catalog']

        self.add_uri(self.catalog, self.ns['RDFS'].isDefinedBy,
                     spec['class']['definition'])
        self._process_class(self.catalog, spec, self.catalog_config,
                            parent=None, allow_empty=False)

    def add_ckan_packages(self, packages):
        """
        Adds all available CKAN packages to the Catalog node.

        :param list of str packages: The list of CKAN package names
        :rtype: None
        """
        for package in packages:
            dataset = URIRef(dcat_config['templates']['identifier']
                             .format(package))

            self.add_uri(dataset, self.ns['RDFS'].isDefinedBy,
                         dcat_config['templates']['dataset_definition']
                         .format(package))
            self.add_uri(dataset, self.ns['RDF'].type,
                         self.ns['DONL']['Dataset'])
            self.add_triple(self.catalog, self.ns['DCAT']['dataset'], dataset)
