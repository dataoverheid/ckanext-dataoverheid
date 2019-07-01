# encoding: utf-8

"""
Entryway for the dataoverheid schema plugin.
"""

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckanext.dataoverheid.validator as validators
import ckanext.dataoverheid.converter as converters
import ckanext.dataoverheid.helper as helper
import ckanext.dataoverheid.schema as schemas

# backwards compatibility fix to read CKAN config settings
if tk.check_ckan_version('2.6', None):
    from ckan.common import config
else:
    import pylons.config as config


class SchemaPlugin(plugins.SingletonPlugin, tk.DefaultDatasetForm):
    """
    This class only implements the CKAN interfaces requires to expose the ckanext/dataoverheid schema functionality into
    CKAN.
    """
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IValidators

    def get_validators(self):
        return helper.merge_dictionaries(validators.get_all(), converters.get_all())

    # IDatasetForm

    def is_fallback(self):
        return config.get('ckan.ckanext-dataoverheid.is_fallback', True)

    def package_types(self):
        return []

    def create_package_schema(self):
        schema = super(SchemaPlugin, self).create_package_schema()
        schema = schemas.get_schema('DCAT-AP-DONL').create_schema(schema)
        schema = schemas.get_schema('DataOverheid').create_schema(schema)

        return schema

    def update_package_schema(self):
        schema = super(SchemaPlugin, self).update_package_schema()
        schema = schemas.get_schema('DCAT-AP-DONL').update_schema(schema)
        schema = schemas.get_schema('DataOverheid').update_schema(schema)

        return schema

    def show_package_schema(self):
        schema = super(SchemaPlugin, self).show_package_schema()
        schema = schemas.get_schema('DCAT-AP-DONL').show_schema(schema)
        schema = schemas.get_schema('DataOverheid').show_schema(schema)

        return schema

    # IPackageController

    def before_index(self, data_dict):
        return helper.transform_multivalued_properties(data_dict)

    def after_show(self, context, data_dict):
        return context, converters.remove_properties(data_dict)
