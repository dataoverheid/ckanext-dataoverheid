# encoding: utf-8

"""
Exposes functionality that affects the authorization of CKAN actions.
"""


from dataset_purge import dataset_purge_authorization


def get_all():
    """
    Retrieves and returns all the authorization methods defined in the ckanext-dataoverheid extension.

    :return: dict, A dictionary containing all the custom authorization functions
    """
    return {
        'dataset_purge': dataset_purge_authorization
    }
