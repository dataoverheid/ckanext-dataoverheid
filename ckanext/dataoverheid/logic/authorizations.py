# encoding: utf-8


import ckan.plugins.toolkit as tk


def dataset_purge_authorization(context, package=None):
    """
    Authorizes the CKAN user which is registered as the `'creator_user_id'` of a CKAN package to perform
    `'dataset_purge'` actions on that dataset.

    :param dict context: The current CKAN context
    :param dict package: The CKAN package to perform the dataset_purge action on

    :return: dict, A dictionary dictating whether or not the user may perform the action
    """
    user = context['user']

    try:
        user_id = tk.get_converter('convert_user_name_or_id_to_id')(user, context)
    except tk.Invalid:
        return {
            'success': False,
            'msg': 'You must be logged-in and be authorized to perform this action'
        }

    try:
        package = tk.get_action('package_show')(context, {'id': package['id']})
    except tk.NotFound:
        return {
            'success': False,
            'msg': 'No package exists with the given id'
        }

    if user_id == package['creator_user_id']:
        return {'success': True}

    return {
        'success': False,
        'msg': 'You are not authorized to perform this action'
    }
