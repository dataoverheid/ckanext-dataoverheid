# encoding: utf-8

"""
Exposes specific validation methods for spatial values.
"""

import re


def valid_epsg28992(key, data, errors, context):
    """
    Checks if a given value conforms to the EPSG28992 spatial notation as defined by OWMS 4.0.

    :param key: tuple, The key containing the value
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    if key not in data:
        return key, data, errors, context

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for val in data[key]:
            if not re.match('^\d{6}(\.\d{3})? \d{6}(\.\d{3})?$', val):
                errors[key].append(u'[{0}] is not a valid EPSG 28992 value'.format(val))

        if len(errors[key]) > 0:
            return key, data, errors, context

    if not re.match('^\d{6}(\.\d{3})? \d{6}(\.\d{3})?$', data[key]):
        errors[key].append(u'[{0}] is not a valid EPSG 28992 value'.format(data[key]))

    return key, data, errors, context


def valid_postcode_huisnummer(key, data, errors, context):
    """
    Checks if a given value conforms to the PostcodeHuisnummer spatial notation as defined by OWMS 4.0.

    :param key: tuple, The key containing the value
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    if key not in data:
        return key, data, errors, context

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for val in data[key]:
            if not re.match('^[1-9]\d{3}([A-Z]{2}(\d+(\S+)?)?)?$', val):
                errors[key].append(u'[{0}] is not a valid PostcodeHuisnummer value'.format(val))

        if len(errors[key]) > 0:
            return key, data, errors, context

    if not re.match('^[1-9]\d{3}([A-Z]{2}(\d+(\S+)?)?)?$', data[key]):
        errors[key].append(u'[{0}] is not a valid PostcodeHuisnummer value'.format(data[key]))

    return key, data, errors, context
