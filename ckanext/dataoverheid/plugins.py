# encoding: utf-8


import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckanext.dataoverheid.logic.converters as converters
import ckanext.dataoverheid.logic.validators as validators
import ckanext.dataoverheid.logic.helpers.transformers as transformers
from ckanext.dataoverheid.logic.schemas import dcat_ap_donl, dataoverheid
from ckanext.dataoverheid.logic.actions import catalog_as_rdf, package_as_rdf
from ckanext.dataoverheid.logic.helpers.queries import wildcard_search
from ckanext.dataoverheid.logic.authorizations import dataset_purge_authorization


if tk.check_ckan_version('2.6', None):
    from ckan.common import config
else:
    import pylons.config as config


class SchemaPlugin(plugins.SingletonPlugin, tk.DefaultDatasetForm):
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IValidators

    def get_validators(self):
        return {
            'convert_list_to_string': converters.convert_list_to_string,
            'convert_string_to_list': converters.convert_string_to_list,
            'default_conversion': converters.default,
            'single_value': validators.single_valued,
            'multi_value': validators.multi_valued,
            'is_string': validators.string,
            'is_bool': validators.boolean,
            'is_uri': validators.uri,
            'is_date': validators.date,
            'is_number': validators.number,
            'controlled_vocabulary': validators.in_vocabulary,
            'taxonomy': validators.in_taxonomy,
            'determine_communities': validators.extract_communities,
            'contact_point': validators.contact_point,
            'temporal': validators.temporal,
            'date_planned': validators.date_planned,
            'legal_foundation': validators.legal_foundation,
            'checksum': validators.checksum,
            'rights': validators.rights,
            'spatial': validators.spatial,
            'epsg_28992': validators.epsg28992,
            'postcode_huisnummer': validators.postcode_huisnummer
        }

    # IDatasetForm

    def is_fallback(self):
        return tk.asbool(config.get('ckan.ckanext-dataoverheid.is_fallback', True))

    def package_types(self):
        return tk.aslist(config.get('ckan.ckanext-dataoverheid.package_types', []))

    def create_package_schema(self):
        schema = super(SchemaPlugin, self).create_package_schema()
        schema = dcat_ap_donl.create_schema(schema)
        schema = dataoverheid.create_schema(schema)

        return schema

    def update_package_schema(self):
        schema = super(SchemaPlugin, self).update_package_schema()
        schema = dcat_ap_donl.update_schema(schema)
        schema = dataoverheid.update_schema(schema)

        return schema

    def show_package_schema(self):
        schema = super(SchemaPlugin, self).show_package_schema()
        schema = dcat_ap_donl.show_schema(schema)
        schema = dataoverheid.show_schema(schema)

        return schema

    # IPackageController

    def before_index(self, data_dict):
        return transformers.transform_multivalued_properties(data_dict)

    def after_show(self, context, data_dict):
        return context, transformers.remove_properties(data_dict)


class RDFPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.interfaces.IActions, inherit=True)
    plugins.implements(plugins.interfaces.IRoutes, inherit=True)

    # IActions

    def get_actions(self):
        return {
            'rdf_catalog_show': catalog_as_rdf,
            'rdf_package_show': package_as_rdf
        }

    # IRoutes

    def before_map(self, _map):
        controller = 'ckanext.dataoverheid.logic.controllers:RDFController'
        output_requirements = {'output': 'xml|rdf|ttl|n3'}

        _map.connect('rdf_catalog', '/catalog.{output}', controller=controller, action='catalog_as_rdf',
                     requirements=output_requirements)
        _map.connect('rdf_package', '/dataset/{package_id}.{output}', controller=controller,
                     action='package_as_rdf', requirements=output_requirements)

        _map.connect('rdf_api_catalog', '/api/3/rdf/catalog.{output}', controller=controller, action='catalog_as_rdf',
                     requirements=output_requirements)
        _map.connect('rdf_api_package', '/api/3/rdf/{package_id}.{output}', controller=controller,
                     action='package_as_rdf', requirements=output_requirements)

        return _map


class InterfacePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets, inherit=True)

    # IConfigurer

    def update_config(self, config):
        tk.add_template_directory(config, 'templates')
        tk.add_resource('fanstatic', 'dataoverheid')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'wildcard_search': wildcard_search
        }

    # IFacets

    def dataset_facets(self, facets_dict, package_type):
        facets_dict.pop('organization', None)
        facets_dict.pop('groups', None)
        facets_dict.pop('tags', None)
        facets_dict.pop('license_id', None)
        facets_dict.pop('res_format', None)

        facets_dict['organization'] = tk._('CKAN Organization')
        facets_dict['groups'] = tk._('CKAN Group')

        facets_dict['facet_authority'] = tk._('donl:authority')
        facets_dict['facet_publisher'] = tk._('donl:publisher')
        facets_dict['facet_source_catalog'] = tk._('donl:sourceCatalog')
        facets_dict['facet_dataset_status'] = tk._('donl:datasetStatus')
        facets_dict['facet_access_rights'] = tk._('donl:accessRights')
        facets_dict['license_id'] = tk._('donl:license')
        facets_dict['res_url'] = tk._('donl:format')

        return facets_dict


class AuthorizationPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions)

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'dataset_purge': dataset_purge_authorization
        }
