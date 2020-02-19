# encoding: utf-8


import ckan.plugins.toolkit as tk
from ckan.lib.base import BaseController
from ckanext.dataoverheid.logic.helpers.config import get_dcat_configuration


class RDFController(BaseController):
    """
    Enables CKAN to create RDF graphs from the CKAN catalog or one of its individual packages.
    """
    def __init__(self):
        """
        Creates a new RDFController and loads the acceptable output formats from the config.
        """
        self.outputs = get_dcat_configuration()['outputs']

    def catalog_as_rdf(self, output):
        """
        Creates a RDF graph from the CKAN catalog.

        :param str output: The output format to use

        :return: any, The created Graph
        """
        tk.response.headers.update({'Content-type': bytes(self.outputs.get(output, 'xml')['content-type'])})

        return tk.get_action('rdf_catalog_show')({}, {
            'output': self.outputs.get(output, 'xml')['output_name']
        })

    def package_as_rdf(self, package_id, output):
        """
        Creates a RDF graph from a CKAN package.

        :param str package_id: The internal id of the CKAN package
        :param str output:     The output format to use

        :return: any, The created Graph
        """
        tk.response.headers.update({'Content-type': bytes(self.outputs.get(output, 'xml')['content-type'])})

        return tk.get_action('rdf_package_show')({}, {
            'id': package_id,
            'output': self.outputs.get(output, 'xml')['output_name']
        })
