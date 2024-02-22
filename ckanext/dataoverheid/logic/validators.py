# encoding: utf-8


from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring
import ckan.plugins.toolkit as tk
from ckanext.dataoverheid.logic.helpers.config import get_config, \
    in_list as in_code_list
from datetime import datetime
from dateutil import parser
import logging
from urllib.parse import urlparse
import re


logger = logging.getLogger('ckanext-dataoverheid')


def single_valued(key, data, errors, context): # noqa
    """
    Ensures that a given value is **not** a list. If a list is found a
    `'StopOnError'` will be raised to instruct CKAN to halt any further
    validation of the value.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    if isinstance(data[key], list):
        errors[key] = [] if not errors[key] else errors[key]
        errors[key].append('expected a single value, got a list of values')
        raise tk.StopOnError


def multi_valued(allow_duplicates=False):
    """
    Generates a function which validates a given value to ensure that it is
    multi valued(a list).

    :param bool allow_duplicates: Whether or not to allow duplicate values in
                                  the list
    :rtype: function
    :return: A function that checks if a given value is multi valued
    """
    def multi_valued_validator(key, data, errors, context):
        """
        Checks if a given value is a list, possibly allowing duplicates. If a
        single string value is given it is converted into a list of size 1. When
        the value is not a list, a `'StopOnError'` will be raised to instruct
        CKAN to halt any further validation of the value.

        :param Any key: Injected by CKAN core
        :param dict[Any, Any] data: Injected by CKAN core
        :param dict[Any, Any] errors: Injected by CKAN core
        :param dict[Any, Any] context: Injected by CKAN core
        :rtype: None
        """
        tk.get_validator('convert_string_to_list')(key, data, errors, context)
        errors[key] = [] if not errors[key] else errors[key]

        if not data[key]:
            return

        value = data[key]

        if isinstance(value, basestring):
            data[key] = [value]

        if isinstance(value, list):
            if not allow_duplicates and len(value) != len(set(value)):
                errors[key].append('duplicates are not allowed')
                raise tk.StopOnError
        else:
            errors[key].append('value must be a list')
            raise tk.StopOnError

    return multi_valued_validator


def string(key, data, errors, context): # noqa
    """
    Ensures that a given value is either a string, or a list of strings. When
    any other type of value is found, a `'StopOnError'` will be raised to
    instruct CKAN to halt any further validation of the value.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]
    string_error = 'expected one or more string values'

    if isinstance(data[key], basestring):
        return

    if isinstance(data[key], list):
        for val in data[key]:
            if not isinstance(val, basestring):
                errors[key].append(string_error)
                raise tk.StopOnError

        return

    errors[key].append(string_error)
    raise tk.StopOnError


def boolean(key, data, errors, context): # noqa
    """
    Ensures that a given value is either a boolean, or a list of booleans. When
    any other type of value is found, a `'StopOnError'` will be raised to
    instruct CKAN to halt any further validation of the value.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    acceptable_values = [True, 'True', 'true', False, 'False', 'false']

    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]
    boolean_error = 'expected a boolean or a list of booleans'

    if isinstance(data[key], list):
        for val in data[key]:
            if val not in acceptable_values:
                errors[key].append(boolean_error)
                raise tk.StopOnError

        return

    if not data[key] in acceptable_values:
        errors[key].append(boolean_error)
        raise tk.StopOnError


def uri(key, data, errors, context): # noqa
    """
    Ensures that a given value is either a URI, or a list of URIs. When any
    other type of value is found, a `'StopOnError'` will be raised to instruct
    CKAN to halt any further validation of the value.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]
    uri_error = 'expected an URI, or a list of URIs'

    if isinstance(data[key], list):
        for input_uri in data[key]:
            parsed = urlparse(input_uri)

            if not all([parsed.scheme, parsed.netloc]):
                errors[key].append(uri_error)
                raise tk.StopOnError

        return

    parsed = urlparse(data[key])

    if not all([parsed.scheme, parsed.netloc]):
        errors[key].append(uri_error)
        raise tk.StopOnError


def date(datetime_format):
    """
    Creates a function which validates datetime objects based on the given
    datetime_format.

    :param str datetime_format: The datetime_format to use for validation
    :rtype: function
    """
    def valid_date(key, data, errors, context): # noqa
        """
        Ensures that a given value is either a datetime, or a list of datetimes.

        When validating against the format `'%Y-%m-%dT%H:%M:%S'` and no valid
        datetime could be constructed, it will attempt to construct a datetime
        based on the `'%Y-%m-%d'` format. Should this succeed, the value will be
        appended with `'T00:00:00'` to ensure all datetimes are stored in the
        exact same format.

        :param Any key: Injected by CKAN core
        :param dict[Any, Any] data: Injected by CKAN core
        :param dict[Any, Any] errors: Injected by CKAN core
        :param dict[Any, Any] context: Injected by CKAN core
        :rtype: None
        """
        if not data[key]:
            return

        date_config = get_config('validation')['dates']
        value = data[key]
        errors[key] = [] if not errors[key] else errors[key]
        date_error = 'expected a date, or a list of dates in format {0}'\
            .format(datetime_format)

        if isinstance(value, list):
            for given_date in value:
                try:
                    datetime.strptime(given_date, datetime_format)
                except ValueError:
                    errors[key].append(date_error)

            return

        try:
            datetime.strptime(value, datetime_format)
        except ValueError:
            if datetime_format != date_config['format']:
                errors[key].append(date_error)

                return

            try:
                datetime.strptime(value, '%Y-%m-%d')
                data[key] = value + date_config['time']
            except ValueError:
                errors[key].append(date_error)

    return valid_date


def number(key, data, errors, context): # noqa
    """
    Ensures that a given value is either a number, or a list of numbers. When
    any other type of value is found, a `'StopOnError'` will be raised to
    instruct CKAN to halt any further validation of the value.

    All numbers encountered must have a value of 1 or higher.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]
    number_error = 'expected a integer, or a a list of integers'
    negative_error = 'integer values may not be less than 1'

    if isinstance(data[key], list):
        for given_number in data[key]:
            try:
                if not int(given_number) > 0:
                    errors[key].append(negative_error)
                    raise tk.StopOnError
            except ValueError:
                errors[key].append(number_error)
                raise tk.StopOnError

        return

    try:
        if not int(data[key]) > 0:
            errors[key].append(negative_error)
            raise tk.StopOnError
    except ValueError:
        errors[key].append(number_error)
        raise tk.StopOnError

    return


def extract_communities(key, data, errors, context): # noqa
    """
    Attempts to determine the community to which this package should belong.

    If a community is already defined in the package, no action will be taken.
    If no authority is found in the package, no action will be taken, as the
    authority of a package is the primary indicator of the designated community.

    If the authority of the package matches one of the authorities defined in a
    community, then that community will be added to the packaged under the multi
    valued `'communities'` key. A package can be part of more than one
    community.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    data[('communities',)] = []
    errors[('communities',)] = []
    communities = []
    tags = []

    for key, value in data.items():
        if len(key) == 3 and key[0] == 'tags' and key[2] == 'name':
            tags.append(value)

    for community in get_config('validation')['communities']:
        [communities.append(community['uri'])
         for prop in community['rules'] if (prop,) in data
         and isinstance(data[(prop,)], list)
         and isinstance(community['rules'][prop], list)
         and any([prop_value in community['rules'][prop]
                  for prop_value in data.get((prop,))])]

        [communities.append(community['uri'])
         for prop in community['rules'] if (prop,) in data
         and isinstance(data[(prop,)], basestring)
         and isinstance(community['rules'][prop], list)
         and data.get((prop,)) in community['rules'][prop]]

        [communities.append(community['uri'])
         for prop in community['rules'] if (prop,) in data
         and isinstance(community['rules'][prop], bool)
         and data.get((prop,)) == community['rules'][prop]]

        try:
            [communities.append(community['uri'])
             for tag in tags if tag in community['tags']]
        except KeyError:
            pass

    communities = list(set(communities))

    for community in communities:
        if in_code_list('DONL:Communities', 'taxonomy', community):
            logger.info('community %s added to dataset', community)
            data[('communities',)].append(community)
        else:
            logger.warning('community %s removed; not in taxonomy', community)


def in_list(name, list_type):
    """
    Exposes a validation method which checks if a given value is present in the
    given list.

    Supported list_types:
     - vocabulary, found in `'ckanext/dataoverheid/resources/vocabularies/'`
     - taxonomy, found in `'ckanext/dataoverheid/resources/taxonomies/'`

    :param str name: The name of the list
    :param str list_type: The type of list
    :rtype: function
    """
    def in_list_validator(key, data, errors, context): # noqa
        """
        Validates a given value or a list of values against a list of acceptable
        values.
    
        :param Any key: Injected by CKAN core
        :param dict[Any, Any] data: Injected by CKAN core
        :param dict[Any, Any] errors: Injected by CKAN core
        :param dict[Any, Any] context: Injected by CKAN core
        :rtype: None
        """
        input_values = data.get(key, None)

        errors[key] = [] if not errors[key] else errors[key]
        list_error = 'value is part of the list ' + name

        if not input_values:
            return

        if isinstance(input_values, list):
            [errors[key].append(list_error)
             for input_value in input_values
             if not in_code_list(name, list_type, input_value)]

            return

        if not in_code_list(name, list_type, str(input_values)):
            errors[key].append(list_error)

        return

    return in_list_validator


def in_vocabulary(name):
    """
    Generates a validation function that can check values against a given
    DCAT-AP-DONL vocabulary.
    
    :param str name: The name of the vocabulary
    :rtype: function
    """
    return in_list(name, 'vocabulary')


def in_taxonomy(name):
    """
    Generates a validation function that can check values against a given
    data.overheid.nl taxonomy.

    :param str name: The name of the taxonomy
    :rtype: function
    """
    return in_list(name, 'taxonomy')


def contact_point(key, data, errors, context): # noqa
    """
    Validates the `'contact_point_*'` values of the CKAN package. A contactPoint
    is considered valid under the following conditions:
     - `contact_point_name` is present and valid
     - `1..n` of [`'contact_point_website'`, `'contact_point_email'`,
       `'contact_point_phone'`] is present and valid
     - all given `'contact_point_*'` properties which are present are also valid

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    message = 'website, email or phone is required for a valid contact_point'
    properties = [
        ('contact_point_website',),
        ('contact_point_email',),
        ('contact_point_phone',)
    ]

    [errors[prop].append(message)
     for prop in properties
     if not any([cp_property in data for cp_property in properties])]


def temporal(key, data, errors, context): # noqa
    """
    Validates the `'temporal_*'` values of the CKAN package. A temporal is
    considered valid under the following conditions:
     - when both `'temporal_start'` and `'temporal_end'` are present, the value
       of `'temporal_start'` is less than `'temporal_end'`
     - all given `'temporal_*'` properties which are present are also valid

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    properties = [
        ('temporal_start',),
        ('temporal_end',)
    ]
    properties_present = (prop in data for prop in properties)
    errors_present = (len(errors[prop]) > 0 for prop in properties)
    message = 'temporal_start cannot be greater or equal to temporal_end'

    if not all(properties_present) or any(errors_present):
        return

    temporal_start = parser.parse(data[('temporal_start',)])
    temporal_end = parser.parse(data[('temporal_end',)])

    [errors[prop].append(message)
     for prop in properties if temporal_start >= temporal_end]

    return


def date_planned(key, data, errors, context):
    """
    When the `'dataset_status'` of a CKAN package is one of
    [`'http://data.overheid.nl/status/gepland'`,
    `'http://data.overheid.nl/status/in_onderzoek'`], then the `'date_planned'`
    property is required and must pass validation.

    No validation is performed whether or not the `'date_planned'` value makes
    'sense'. It can be a value representing a point in time in the past, present
    or future.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    properties = [
        ('dataset_status',),
        ('date_planned',)
    ]
    errors_present = (len(errors[prop]) > 0 for prop in properties)
    affected_states = get_config('validation')['date_planned_states']

    if not properties[0] in data or any(errors_present):
        return key, data, errors, context

    try:
        data.get(properties[1])
    except KeyError:
        error_message = 'value is required when dataset_status is one of {0}'\
            .format(', '.join(affected_states))
        [errors[properties[1]].append(error_message)
         for data[properties[0]] in affected_states]

    return key, data, errors, context


def legal_foundation(key, data, errors, context): # noqa
    """
    Validates the `'legal_foundation_*'` values of the CKAN package. A
    legalFoundation is considered valid under the following conditions:
     - when any one of the `'legal_foundation_*'` properties is present, all
       other `'legal_foundation_*'` properties must also be present
     - all given `'legal_foundation_*'` properties which are present are also
       valid

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    properties = [
        ('legal_foundation_ref',),
        ('legal_foundation_uri',),
        ('legal_foundation_label',)
    ]
    properties_present = (prop in data for prop in properties)
    errors_present = (len(errors[prop]) > 0 for prop in properties)
    message_format = '{0} is required when providing a legal_foundation'

    if not any(properties_present) or any(errors_present):
        return

    [errors[absentee].append(message_format.format(absentee[0]))
     for absentee in [prop for prop in properties if prop not in data]]

    return


def checksum(key, data, errors, context):
    """
    Validates the `'checksum'` values of the CKAN package. A checksum is
    considered valid under the following conditions:
     - when either `hash` or `hash_algorithm` is present, the other must too be
       present
     - all given `'hash'` properties which are present are also valid

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    hash_tuple = ('resources', key[1], 'hash')

    if hash_tuple in data and data[hash_tuple] == '':
        data.pop(hash_tuple, None)
        errors.pop(hash_tuple, None)

    properties = [hash_tuple, ('resources', key[1], 'hash_algorithm')]
    properties_present = (prop in data for prop in properties if prop)
    message_format = '{0} is required when providing a valid checksum'

    if not any(properties_present):
        return key, data, errors, context

    if not all(properties_present):
        for prop in properties:
            errors[prop].append(message_format.format(prop[2]))

    return key, data, errors, context


def rights(key, data, errors, context):
    """
    Validates the rights statements of the CKAN package. It states that when
    dataset_status is 'beschikbaar' and access_rights is 'PUBLIC' that an open
    license must be provided.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    dataset_status = data.get(('dataset_status',), None)
    access_rights = data.get(('access_rights',), None)
    license = data.get(('license_id',), None)
    validation_config = get_config('validation')

    available_uri = validation_config['available_uri']
    public_uri = validation_config['public_uri']

    status_is_available = dataset_status == available_uri
    access_rights_public = access_rights == public_uri
    license_is_open = license not in validation_config['non_open_licenses']

    if status_is_available and access_rights_public and not license_is_open:
        errors[('license_id',)] = [
            'When dataset_status is set to ' + available_uri + ' and '
            'access_rights is set to [ ' + public_uri + ' ], an open license '
            'must be provided; got ' + license
        ]

    return key, data, errors, context


def spatial(key, data, errors, context): # noqa
    """
    Validates that all the given `'spatial_values'` are validate according to
    their accompanied `'spatial_scheme'`. Since all `'spatial_value'`s are
    validated against such a `'spatial_scheme'` this means that both lists
    should be of the exact same size.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    properties = [('spatial_scheme',), ('spatial_value',)]
    properties_present = (prop in data for prop in properties)

    if not any(properties_present):
        return

    if any((len(errors[prop]) > 0 for prop in properties)):
        return

    if not all(properties_present):
        [errors[absentee].append(absentee[0] + ' is required for spatial')
         for absentee in [prop for prop in properties if prop not in data]]

        return

    schemes = data[('spatial_scheme',)]
    values = data[('spatial_value',)]

    if len(schemes) != len(values):
        [errors[prop].append('the list of schemes must be of the same size as '
                             'the list of values')
         for prop in properties]

        return

    spatial_config = get_config('validation')['spatial']
    validator_mapping = {}

    for scheme_uri, mapping in spatial_config.items():
        validator = mapping['validator']

        try:
            validator = validator(mapping['argument'])
        except KeyError:
            pass

        validator_mapping.update({scheme_uri: validator})

    message = 'spatial_value {0} is not valid according to scheme {1}'
    [errors[('spatial_value',)].append(message.format(val, schemes[iterator]))
     for iterator, val in enumerate(values) if
     not _valid_spatial(validator_mapping[schemes[iterator]], val)]


def _valid_spatial(validation_method, value):
    """
    Executes a given validation method and returns whether or not any validation
    messages were generated.

    :param function validation_method: The validation method to execute
    :param Any value: The value to validate
    :rtype: bool
    """
    errors = {'value': []}
    validation_method('value', {'value': value}, errors, {})

    return len(errors['value']) == 0


def epsg28992(key, data, errors, context): # noqa
    """
    Validates that a given value is valid according to the EPSG:28992 coordinate
    reference system.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    if key not in data:
        return

    pattern = get_config('validation')['regex']['epsg28992']
    error_message = 'value is not a valid Overheid:PostcodeHuisnummer'
    errors[key] = [] if not errors[key] else errors[key]
    _regex_match(key, data[key], pattern, errors, error_message)


def postcode_huisnummer(key, data, errors, context): # noqa
    """
    Validates that a given value is valid according to the
    Overheid:PostcodeHuisnummer reference system.

    :param Any key: Injected by CKAN core
    :param dict[Any, Any] data: Injected by CKAN core
    :param dict[Any, Any] errors: Injected by CKAN core
    :param dict[Any, Any] context: Injected by CKAN core
    :rtype: None
    """
    if key not in data:
        return

    pattern = get_config('validation')['regex']['postcodeHuisnummer']
    error_message = 'value is not a valid Overheid:PostcodeHuisnummer'
    errors[key] = [] if not errors[key] else errors[key]
    _regex_match(key, data[key], pattern, errors, error_message)


def _regex_match(key, value, pattern, errors, error_message):
    """
    Validates that a given value adheres to a given regex pattern.

    :param Any key: The name of the value
    :param str|list of str value: The value itself
    :param str pattern: The pattern the value must match
    :param dict[Any, Any] errors: The error dictionary of CKAN
    :param str error_message: The error message should the value not match the
                              pattern
    :rtype: None
    """
    if isinstance(value, list):
        [errors[key].append(error_message) for val in value
         if not re.match(pattern, val)]

        return

    if not re.match(pattern, value):
        errors[key].append(error_message)
