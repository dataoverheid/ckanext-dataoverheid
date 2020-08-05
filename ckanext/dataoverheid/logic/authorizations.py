# encoding: utf-8


import ckan.plugins.toolkit as tk


def dataset_purge_authorization(context, package=None):
    """
    Authorizes the CKAN user which is registered as the `'creator_user_id'` of a
    CKAN package to perform `'dataset_purge'` actions on that dataset.

    :param dict[str, Any] context: The current CKAN context
    :param dict[str, Any] package: The CKAN package to perform the dataset_purge
                                   action on
    :rtype dict[str, Any]:
    """
    user = context['user']
    user_to_user_id = tk.get_converter('convert_user_name_or_id_to_id')
    package_show = tk.get_action('package_show')

    try:
        user_id = user_to_user_id(user, context)
        package = package_show(context, {'id': package['id']})

        if user_id == package['creator_user_id']:
            return {
                'success': True
            }

        return {
            'success': False,
            'msg': 'You must be authorized to perform this action'
        }
    except tk.Invalid:
        return {
            'success': False,
            'msg': 'You must be authorized to perform this action'
        }
    except tk.NotFound:
        return {
            'success': False,
            'msg': 'No package exists with the given id'
        }
