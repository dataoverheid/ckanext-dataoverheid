# encoding: utf-8

"""
Exposes schema modifications for CKAN packages and resources.
"""

import dcat_ap_donl_schema
import dataoverheid_schema


_SCHEMAS = {
    'DCAT-AP-DONL': dcat_ap_donl_schema,
    'DataOverheid': dataoverheid_schema
}


def get_schema(name):
    """
    Return a specific schema defined by this extension.

    :param name: The name of the schema to retrieve
    :return: The schema module that corresponds with the given name
    """
    try:
        return _SCHEMAS[name]
    except KeyError:
        raise Exception(u'No schema defined with name [{0}]'.format(name))
