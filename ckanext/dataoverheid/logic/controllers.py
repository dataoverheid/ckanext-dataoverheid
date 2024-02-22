# encoding: utf-8


from builtins import bytes
import ckan.plugins.toolkit as tk
from ckan.lib.base import BaseController
from ckanext.dataoverheid.logic.helpers.config import get_config


class RDFController(BaseController):
    """
    Enables CKAN to create RDF graphs from the CKAN catalog or one of its
    individual packages.
    """
    def __init__(self):
        """
        Creates a new RDFController and loads the acceptable output formats from
        the config.
        """
        self.outputs = get_config('dcat')['outputs']

    def catalog_as_rdf(self, output):
        """
        Creates a RDF graph from the CKAN catalog.

        :param str output: The output format to use
        :rtype: Any
        :return: The created Graph
        """
        output_contents = self.outputs.get(output, 'xml')

        tk.response.headers.update(
            {'Content-type': bytes(output_contents['content-type'])}
        )

        return tk.get_action('rdf_catalog_show')({}, {
            'output': output_contents['output_name']
        })

    def package_as_rdf(self, package_id, output):
        """
        Creates a RDF graph from a CKAN package.

        :param str package_id: The internal id of the CKAN package
        :param str output: The output format to use
        :rtype: Any
        :return: The created Graph
        """
        output_contents = self.outputs.get(output, 'xml')

        tk.response.headers.update(
            {'Content-type': bytes(output_contents['content-type'])}
        )

        return tk.get_action('rdf_package_show')({}, {
            'id': package_id,
            'output': output_contents['output_name']
        })
