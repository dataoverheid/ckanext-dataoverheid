# encoding: utf-8

from ckanext.dataoverheid.helper import get_communities


def extract_communities(key, data, errors, context):
    """

    :param key:
    :param data:
    :param errors:
    :param context:
    :return:
    """
    if ('communities',) in data and data.get(('communities',)):
        return key, data, errors, context

    if not ('authority',) in data:
        return key, data, errors, context

    data[('communities',)] = []
    errors[('communities',)] = []
    authority = data.get(('authority',), None)

    for community in get_communities():
        if authority and authority in community['authority']:
            data[('communities',)].append(community['uri'])

    return key, data, errors, context
