# encoding: utf-8


from ckanext.dataoverheid.logic.rdf.graph_builder import DatasetDCATGraphBuilder, CatalogDCATGraphBuilder
import ckan.plugins.toolkit as tk
from ckan.lib.redis import connect_to_redis
from datetime import datetime


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
    Generates a RDF graph from the CKAN catalog. The output of the Graph is cached in Redis for up to 24 hours. This
    cache will be used on any subsequent request for the Graph.

    :param dict context:   The current CKAN context
    :param dict data_dict: Injected by CKAN, not used

    :return: any, The Graph, in the requested output format
    """
    current_date = str(datetime.strftime(datetime.now(), '%Y%m%d'))
    cache_key = 'ckanext.dataoverheid:rdf._cache_date'

    if redis_conn.exists(cache_key) and current_date == redis_conn.get(cache_key):
        return redis_conn.get('ckanext.dataoverheid:rdf.catalog_' + data_dict.get('output'))

    packages = tk.get_action('package_list')(context, {})

    graph = CatalogDCATGraphBuilder()
    graph.add_ckan_packages(packages)

    redis_conn.set('ckanext.dataoverheid:rdf._cache_date', current_date)
    redis_conn.set('ckanext.dataoverheid:rdf.catalog_xml', graph.as_('xml'))
    redis_conn.set('ckanext.dataoverheid:rdf.catalog_rdf', graph.as_('xml'))
    redis_conn.set('ckanext.dataoverheid:rdf.catalog_ttl', graph.as_('n3'))
    redis_conn.set('ckanext.dataoverheid:rdf.catalog_n3', graph.as_('n3'))

    return redis_conn.get('ckanext.dataoverheid:rdf.catalog_' + data_dict.get('output', 'xml'))


redis_conn = connect_to_redis()
