# encoding: utf-8

"""
Exposes validation messages targeting the datatype of properties.
"""

from urlparse import urlparse
from datetime import datetime
import ckan.plugins.toolkit as tk

# backwards compatibility fix to use StopOnError
if tk.check_ckan_version('2.6', None):
    from ckan.plugins.toolkit import StopOnError
else:
    from ckan.lib.navl.dictization_functions import StopOnError


def single_valued(key, data, errors, context):
    """
    Checks if a given value is not a list.

    :param key: tuple, The key containing the value
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    if isinstance(data[key], list):
        errors[key] = [] if not errors[key] else errors[key]
        errors[key].append(u'value must be single valued; got [list]')
        raise StopOnError

    return key, data, errors, context


def multi_valued(allow_duplicates=False):
    """
    Generates a function which validates a given value to ensure that it is multi valued(a list).

    :param allow_duplicates: bool, Whether or not to allow duplicate values in the list
    :return: func, A function that checks if a given value is multi valued
    """
    def multi_valued_validator(key, data, errors, context):
        """
        Checks if a given value is a list, possibly allowing duplicates. If a single value is given it is converted into a
        list of size 1.

        :param key: tuple, The key containing the value
        :param data: dict, The data dictionary representing the package
        :param errors: dict, The validation errors so far
        :param context: dict, The current CKAN context
        :return: The original, possibly modified, arguments
        """
        convert_string_to_list = tk.get_validator('convert_string_to_list')
        key, data, errors, context = convert_string_to_list(key, data, errors, context)
        errors[key] = [] if not errors[key] else errors[key]

        if not data[key]:
            return key, data, errors, context

        if isinstance(data[key], basestring):
            data[key] = [data[key]]

        if isinstance(data[key], list):
            if not allow_duplicates:
                if len(data[key]) != len(set(data[key])):
                    errors[key].append(
                        u'duplicate values are not allowed; got [{0}]'.format(data[key])
                    )

            return key, data, errors, context

        errors[key].append(u'value must be multi valued; got [{0}]'.format(data[key]))
        raise StopOnError

    return multi_valued_validator


def string(key, data, errors, context):
    """
    Checks if a given value is a basestring or a list of basestrings.

    :param key: tuple, The key containing the value
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    if not data[key]:
        return key, data, errors, context

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], basestring):
        return key, data, errors, context

    if isinstance(data[key], list):
        for val in data[key]:
            if not isinstance(val, basestring):
                errors[key].append(u'expected a string, or a list of strings; got [{0}]'.format(val))
                raise StopOnError

        return key, data, errors, context

    errors[key].append(u'expected a string, or a list of strings; got [{0}]'.format(data[key]))
    raise StopOnError


def boolean(key, data, errors, context):
    """
    Checks if a given value is a boolean or a list of booleans.

    :param key: tuple, The key containing the value
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    acceptable_values = [True, 'True', 'true', False, 'False', 'false']

    if not data[key]:
        return key, data, errors, context

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for val in data[key]:
            if val not in acceptable_values:
                errors[key].append(u'expected a boolean; got [{0}]'.format(data[key]))
                raise StopOnError

        return key, data, errors, context

    if data[key] in acceptable_values:
        return key, data, errors, context

    errors[key].append(u'expected a boolean, or a list of booleans; got [{0}]'.format(data[key]))
    raise StopOnError


def uri(key, data, errors, context):
    """
    Checks if a given value is a URI or a list of URIs.

    :param key: tuple, The key containing the value
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    if not data[key]:
        return key, data, errors, context

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for input_uri in data[key]:
            parsed = urlparse(input_uri)

            if not all([parsed.scheme, parsed.netloc]):
                errors[key].append(u'expected an uri; got [{0}]'.format(input_uri))
                raise StopOnError

        return key, data, errors, context

    parsed = urlparse(data[key])

    if not all([parsed.scheme, parsed.netloc]):
        errors[key].append(u'expected an uri; got [{0}]'.format(data[key]))
        raise StopOnError

    return key, data, errors, context


def date(datetime_format):
    """
    Creates a function which validates datetime objects based on the given datetime_format.

    :param datetime_format: The datetime_format to use for validation
    :return: function, the validation function
    """
    def valid_date(key, data, errors, context):
        """
        Checks if a given value is a datetime or a list of datetimes.

        :param key: tuple, The key containing the value
        :param data: dict, The data dictionary representing the package
        :param errors: dict, The validation errors so far
        :param context: dict, The current CKAN context
        :return: The original, possibly modified, arguments
        """
        if not data[key]:
            return key, data, errors, context

        errors[key] = [] if not errors[key] else errors[key]

        if isinstance(data[key], list):
            for given_date in data[key]:
                try:
                    datetime.strptime(given_date, datetime_format)
                except ValueError:
                    errors[key].append(
                        u'expected date with format [{0}]; got [{1}]'.format(datetime_format, given_date)
                    )

            return key, data, errors, context

        try:
            datetime.strptime(data[key], datetime_format)
        except ValueError:
            if datetime_format != '%Y-%m-%dT%H:%M:%S':
                errors[key].append(
                    u'expected date with format [{0}]; got [{1}]'.format(datetime_format, data[key])
                )

                return key, data, errors, context

            try:
                datetime.strptime(data[key], '%Y-%m-%d')
                data[key] = data[key] + 'T00:00:00'
            except ValueError:
                errors[key].append(
                    u'expected date with format [{0}]; got [{1}]'.format(datetime_format, data[key])
                )

        return key, data, errors, context

    return valid_date


def number(key, data, errors, context):
    """
    Checks if a given value is a positive integer or a list of positive integers.

    :param key: tuple, The key containing the value
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    if not data[key]:
        return key, data, errors, context

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for given_number in data[key]:
            try:
                val = int(given_number)

                if not val > 0:
                    errors[key].append(u'expected a positive integer; got [{0}]'.format(val))
                    raise StopOnError
            except ValueError:
                errors[key].append(u'expected a positive integer; got [{0}]'.format(given_number))
                raise StopOnError

        return key, data, errors, context

    try:
        val = int(data[key])

        if not val > 0:
            errors[key].append(u'expected a positive integer; got [{0}]'.format(val))
            raise StopOnError
    except ValueError:
        errors[key].append(u'expected a positive integer; got [{0}]'.format(data[key]))
        raise StopOnError

    return key, data, errors, context
