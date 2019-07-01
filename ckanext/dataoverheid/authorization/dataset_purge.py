# encoding: utf-8

"""
Contains functionality that affects the authorization of performing dataset_purge actions.
"""


import ckan.plugins.toolkit as tk
import logging


logger = logging.getLogger('ckanext.dataoverheid')


def dataset_purge_authorization(context, package=None):
    """
    Allows the creator of a CKAN package to perform dataset_purge actions, regardless of the role of the CKAN user.

    :param context: dict, The current CKAN context
    :param package: dict, The CKAN package to perform the dataset_purge action on
    :return: dict, A dictionary dictating whether or not the user may perform the action
    """
    user = context['user']

    try:
        user_id = tk.get_converter('convert_user_name_or_id_to_id')(user, context)
    except tk.Invalid:
        logging.info(u'dataset_purge_authorization: user is not logged in; authorization failed')
        return {
            'success': False,
            'msg': u'You must be logged-in and be authorized to perform this action'
        }

    try:
        package = tk.get_action('package_show')(context, {'id': package['id']})
    except tk.NotFound:
        logging.info(u'dataset_purge_authorization: package to purge does not exist; authorization failed')
        return {
            'success': False,
            'msg': u'No package exists with the given id'
        }

    if user_id == package['creator_user_id']:
        logging.info(u'dataset_purge_authorization: user_id matches creator_user_id; authorization given')
        return {'success': True}

    logging.info(u'dataset_purge_authorization: user_id does not match creator_user_id; authorization failed')
    return {
        'success': False,
        'msg': u'You are not authorized to perform this action'
    }
