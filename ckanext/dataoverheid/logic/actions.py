# encoding: utf-8


import ckan.plugins.toolkit as tk
from ckanext.dataoverheid.logic.rdf.graph_builder import DatasetDCATGraphBuilder, CatalogDCATGraphBuilder


@tk.side_effect_free
def package_as_rdf(context, data_dict=None):
    """
    Generates a RDF graph from a given CKAN package.

    :param dict context:   The current CKAN context
    :param dict data_dict: The package to model

    :return: any, The Graph, in the requested output format
    """
    package = tk.get_action('package_show')(context, data_dict)

    graph = DatasetDCATGraphBuilder(package['name'])
    graph.parse_ckan_package(package)

    return graph.as_(data_dict.get('output', 'xml'))


@tk.side_effect_free
def catalog_as_rdf(context, data_dict=None):
    """
    Generates a RDF graph from the CKAN catalog.

    :param dict context:   The current CKAN context
    :param dict data_dict: Injected by CKAN, not used

    :return: any, The Graph, in the requested output format
    """
    packages = tk.get_action('package_list')(context, {})

    graph = CatalogDCATGraphBuilder()
    graph.add_ckan_packages(packages)

    return graph.as_(data_dict.get('output', 'xml'))
