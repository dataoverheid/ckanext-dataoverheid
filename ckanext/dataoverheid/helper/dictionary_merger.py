# encoding: utf-8

"""
Exposes functionality which allows dictionaries to be merged.
"""


def merge_dictionaries(first, second):
    """
    Merges two dictionaries and returns the merged dictionary.

    :param first: dict, The dictionary to merge
    :param second: dict, The dictionary to merge
    :return: dict, The merged dictionary
    """
    merged = first.copy()
    merged.update(second)

    return merged
