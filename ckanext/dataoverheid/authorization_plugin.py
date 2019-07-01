# encoding: utf-8

"""
Entryway for the dataoverheid authorization plugin.
"""

import ckan.plugins as plugins
import ckanext.dataoverheid.authorization as authorization


class AuthorizationPlugin(plugins.SingletonPlugin):
    """
    This class only implements the CKAN interfaces requires to expose the ckanext/dataoverheid authorization
    functionality into CKAN.
    """
    plugins.implements(plugins.IAuthFunctions)

    # IAuthFunctions

    def get_auth_functions(self):
        return authorization.get_all()
