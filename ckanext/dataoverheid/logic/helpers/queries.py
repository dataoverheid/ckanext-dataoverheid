# encoding: utf-8


import ckan.plugins.toolkit as tk


def wildcard_search(rows=0):
    """
    Initiates a wildcard `package_search`, returning the result of the search
    action with the specified amount of rows.

    :param int rows: The amount of records to return
    :rtype: dict[Any, Any],
    :return: The search results
    """
    return tk.get_action('package_search')({}, {
        'q': '*:*',
        'rows': rows,
        'sort': 'metadata_modified desc',
        'facet': True,
        'facet.field': [
            'authority',
            'source_catalog'
        ],
        'facet.mincount': 1,
        'facet.limit': -1
    })
