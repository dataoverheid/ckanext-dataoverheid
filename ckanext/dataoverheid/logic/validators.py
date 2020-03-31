# encoding: utf-8


import ckan.plugins.toolkit as tk
from ckan.plugins.toolkit import StopOnError
from ckanext.dataoverheid.logic.helpers.config import get_validation_configuration, in_list as in_code_list
from datetime import datetime
from dateutil import parser
import logging
from urlparse import urlparse
import re


logger = logging.getLogger('ckanext-dataoverheid')


def single_valued(key, data, errors, context):
    """
    Ensures that a given value is **not** a list. If a list is found a `'StopOnError'` will be raised to instruct CKAN
    to halt any further validation of the value.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://docs.ckan.org/en/latest/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.StopOnError

    :param tuple key: Injected by CKAN core
    :param dict data: Injected by CKAN core
    :param dict errors: Injected by CKAN core
    :param dict context: Injected by CKAN core
    :rtype: None
    """
    if isinstance(data[key], list):
        errors[key] = [] if not errors[key] else errors[key]
        errors[key].append('value must be single valued; got [list]')
        raise StopOnError


def multi_valued(allow_duplicates=False):
    """
    Generates a function which validates a given value to ensure that it is multi valued(a list).

    :param bool allow_duplicates: Whether or not to allow duplicate values in the list
    :rtype: function
    :return: A function that checks if a given value is multi valued
    """
    def multi_valued_validator(key, data, errors, context):
        """
        Checks if a given value is a list, possibly allowing duplicates. If a single string value is given it is
        converted into a list of size 1. When the value is not a list, a `'StopOnError'` will be raised to instruct CKAN
        to halt any further validation of the value.

        See also:
         - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
         - https://docs.ckan.org/en/latest/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.StopOnError

        :param tuple key: Injected by CKAN core
        :param dict data: Injected by CKAN core
        :param dict errors: Injected by CKAN core
        :param dict context: Injected by CKAN core
        :rtype: None
        """
        tk.get_validator('convert_string_to_list')(key, data, errors, context)
        errors[key] = [] if not errors[key] else errors[key]

        if not data[key]:
            return

        if isinstance(data[key], basestring):
            data[key] = [data[key]]

        if isinstance(data[key], list) and not allow_duplicates and len(data[key]) != len(set(data[key])):
            errors[key].append('duplicate values are not allowed; got [{0}]'.format(data[key]))
            raise StopOnError

        if not isinstance(data[key], list):
            errors[key].append('value must be multi valued; got [{0}]'.format(data[key]))
            raise StopOnError

    return multi_valued_validator


def string(key, data, errors, context):
    """
    Ensures that a given value is either a string, or a list of strings. When any other type of value is found, a
    `'StopOnError'` will be raised to instruct CKAN to halt any further validation of the value.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://docs.ckan.org/en/latest/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.StopOnError

    :param tuple key: Injected by CKAN core
    :param dict data: Injected by CKAN core
    :param dict errors: Injected by CKAN core
    :param dict context: Injected by CKAN core
    :rtype: None
    """
    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], basestring):
        return

    if isinstance(data[key], list):
        for val in data[key]:
            if not isinstance(val, basestring):
                errors[key].append('expected a string, or a list of strings; got [{0}]'.format(val))
                raise StopOnError

        return

    errors[key].append('expected a string, or a list of strings; got [{0}]'.format(data[key]))
    raise StopOnError


def boolean(key, data, errors, context):
    """
    Ensures that a given value is either a boolean, or a list of booleans. When any other type of value is found, a
    `'StopOnError'` will be raised to instruct CKAN to halt any further validation of the value.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://docs.ckan.org/en/latest/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.StopOnError

    :param tuple key: Injected by CKAN core
    :param dict data: Injected by CKAN core
    :param dict errors: Injected by CKAN core
    :param dict context: Injected by CKAN core
    :rtype: None
    """
    acceptable_values = [True, 'True', 'true', False, 'False', 'false']

    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for val in data[key]:
            if val not in acceptable_values:
                errors[key].append('expected a boolean; got [{0}]'.format(data[key]))
                raise StopOnError

        return

    if data[key] in acceptable_values:
        return

    errors[key].append('expected a boolean, or a list of booleans; got [{0}]'.format(data[key]))
    raise StopOnError


def uri(key, data, errors, context):
    """
    Ensures that a given value is either a URI, or a list of URIs. When any other type of value is found, a
    `'StopOnError'` will be raised to instruct CKAN to halt any further validation of the value.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://docs.ckan.org/en/latest/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.StopOnError

    :param tuple key: Injected by CKAN core
    :param dict data: Injected by CKAN core
    :param dict errors: Injected by CKAN core
    :param dict context: Injected by CKAN core
    :rtype: None
    """
    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for input_uri in data[key]:
            parsed = urlparse(input_uri)

            if not all([parsed.scheme, parsed.netloc]):
                errors[key].append('expected an uri; got [{0}]'.format(input_uri))
                raise StopOnError

        return

    parsed = urlparse(data[key])

    if not all([parsed.scheme, parsed.netloc]):
        errors[key].append('expected an uri; got [{0}]'.format(data[key]))
        raise StopOnError

    return


def date(datetime_format):
    """
    Creates a function which validates datetime objects based on the given datetime_format.

    :param str datetime_format: The datetime_format to use for validation
    :rtype: function
    :return: The validation function
    """
    def valid_date(key, data, errors, context):
        """
        Ensures that a given value is either a datetime, or a list of datetimes. When any other type of value is found,
        a `'StopOnError'` will be raised to instruct CKAN to halt any further validation of the value.

        When validating against the format `'%Y-%m-%dT%H:%M:%S'` and no valid datetime could be constructed, it will
        attempt to construct a datetime based on the `'%Y-%m-%d'` format. Should this succeed, the value will be
        appended with `'T00:00:00'` to ensure all datetimes are stored in the exact same format.

        See also:
         - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
         - https://docs.ckan.org/en/latest/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.StopOnError

        :param tuple key: Injected by CKAN core
        :param dict data: Injected by CKAN core
        :param dict errors: Injected by CKAN core
        :param dict context: Injected by CKAN core
        :rtype: None
        """
        if not data[key]:
            return

        errors[key] = [] if not errors[key] else errors[key]

        if isinstance(data[key], list):
            for given_date in data[key]:
                try:
                    datetime.strptime(given_date, datetime_format)
                except ValueError:
                    errors[key].append('expected date with format [{0}]; got [{1}]'.format(datetime_format, given_date))

            return

        try:
            datetime.strptime(data[key], datetime_format)
        except ValueError:
            if datetime_format != '%Y-%m-%dT%H:%M:%S':
                errors[key].append('expected date with format [{0}]; got [{1}]'.format(datetime_format, data[key]))

                return

            try:
                datetime.strptime(data[key], '%Y-%m-%d')
                data[key] = '{0}T00:00:00'.format(data[key])
            except ValueError:
                errors[key].append('expected date with format [{0}]; got [{1}]'.format(datetime_format, data[key]))

        return

    return valid_date


def number(key, data, errors, context):
    """
    Ensures that a given value is either a number, or a list of numbers. When any other type of value is found, a
    `'StopOnError'` will be raised to instruct CKAN to halt any further validation of the value.

    All numbers encountered must have a value of 1 or higher.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://docs.ckan.org/en/latest/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.StopOnError

    :param tuple key: Injected by CKAN core
    :param dict data: Injected by CKAN core
    :param dict errors: Injected by CKAN core
    :param dict context: Injected by CKAN core
    :rtype: None
    """
    if not data[key]:
        return

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        for given_number in data[key]:
            try:
                if not int(given_number) > 0:
                    errors[key].append('expected a positive integer; got [{0}]'.format(given_number))
                    raise StopOnError
            except ValueError:
                errors[key].append('expected a positive integer; got [{0}]'.format(given_number))
                raise StopOnError

        return

    try:
        if not int(data[key]) > 0:
            errors[key].append('expected a positive integer; got [{0}]'.format(data[key]))
            raise StopOnError
    except ValueError:
        errors[key].append('expected a positive integer; got [{0}]'.format(data[key]))
        raise StopOnError

    return


def extract_communities(key, data, errors, context):
    """
    Attempts to determine the community to which this package should belong.

    If a community is already defined in the package, no action will be taken. If no authority is found in the package,
    no action will be taken, as the authority of a package is the primary indicator of the designated community.

    If the authority of the package matches one of the authorities defined in a community, then that community will be
    added to the packaged under the multi valued `'communities'` key. A package can be part of more than one community.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators

    :param tuple key: Injected by CKAN core
    :param dict data: Injected by CKAN core
    :param dict errors: Injected by CKAN core
    :param dict context: Injected by CKAN core
    :rtype: None
    """
    data[('communities',)] = []
    errors[('communities',)] = []
    communities = []
    tags = []

    for key, value in data.iteritems():
        if len(key) == 3 and key[0] == 'tags' and key[2] == 'name':
            tags.append(value)

    for community in get_validation_configuration()['communities']:
        [communities.append(community['uri']) for prop in community['rules'] if (prop,) in data
         and isinstance(data[(prop,)], list) and isinstance(community['rules'][prop], list)
         and any(prop_value in community['rules'][prop] for prop_value in data.get((prop,)))]

        [communities.append(community['uri']) for prop in community['rules'] if (prop,) in data
         and isinstance(data[(prop,)], basestring) and isinstance(community['rules'][prop], list)
         and data.get((prop,)) in community['rules'][prop]]

        [communities.append(community['uri']) for prop in community['rules'] if (prop,) in data
         and isinstance(community['rules'][prop], bool) and data.get((prop,)) == community['rules'][prop]]

        try:
            [communities.append(community['uri']) for tag in tags if tag in community['tags']]
        except KeyError:
            logger.info('no community extraction based on tags; no rules defined for community %s', community['uri'])

    communities = list(set(communities))

    for community in communities:
        if in_code_list('DONL:Communities', 'taxonomy', community):
            logger.info('community [ %s ] added to dataset', community)

            data[('communities',)].append(community)
        else:
            logger.warning('community [ %s ] removed; not part of the taxonomy', community)


def in_list(name, list_type):
    """
    Exposes a validation method which checks if a given value is present in the given list.

    :param str name:      The name of the list
    :param str list_type: The type of list
    
    Support list_types:
     - vocabulary, found in `'ckanext/dataoverheid/resources/vocabularies/*'`
     - taxonomy, found in `'ckanext/dataoverheid/resources/taxonomies/*'`

    :return: function, The validation function
    """
    def in_list_validator(key, data, errors, context):
        """
        Validates a given value or a list of values against a list of acceptable values.
    
        See also:
         - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
         - https://waardelijsten.dcat-ap-donl.nl
    
        :param tuple key:    Injected by CKAN core
        :param dict data:    Injected by CKAN core
        :param dict errors:  Injected by CKAN core
        :param dict context: Injected by CKAN core
    
        :return: void
        """
        input_values = data.get(key, None)

        errors[key] = [] if not errors[key] else errors[key]

        if not input_values:
            return

        if isinstance(input_values, list):
            [errors[key].append('value [{0}] is not part of list [{1}]'.format(input_value, name))
             for input_value in input_values if not in_code_list(name, list_type, input_value)]

            return

        if not in_code_list(name, list_type, str(input_values)):
            errors[key].append('value [{0}] is not part of list [{1}]'.format(input_values, name))

        return

    return in_list_validator


def in_vocabulary(name):
    """
    Generates a validation function that can check values against a given DCAT-AP-DONL vocabulary.
    
    :param str name: The name of the vocabulary
    
    :return: function, The vocabulary validation function
    """
    return in_list(name, 'vocabulary')


def in_taxonomy(name):
    """
    Generates a validation function that can check values against a given data.overheid.nl taxonomy.

    :param str name: The name of the taxonomy

    :return: function, The taxonomy validation function
    """
    return in_list(name, 'taxonomy')


def contact_point(key, data, errors, context):
    """
    Validates the `'contact_point_*'` values of the CKAN package. A contactPoint is considered valid under the following
    conditions:
     - `contact_point_name` is present and valid
     - `1..n` of [`'contact_point_website'`, `'contact_point_email'`, `'contact_point_phone'`] is present and valid
     - all given `'contact_point_*'` properties which are present are also valid

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    properties = [
        ('contact_point_website',),
        ('contact_point_email',),
        ('contact_point_phone',)
    ]

    [errors[prop].append('website, email or phone is required for a valid contact_point')
     for prop in properties if not any([cp_property in data for cp_property in properties])]

    return


def temporal(key, data, errors, context):
    """
    Validates the `'temporal_*'` values of the CKAN package. A temporal is considered valid under the following
    conditions:
     - when both `'temporal_start'` and `'temporal_end'` are present, the value of `'temporal_start'` is less than 
       `'temporal_end'`
     - all given `'temporal_*'` properties which are present are also valid

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    properties = [
        ('temporal_start',),
        ('temporal_end',)
    ]
    properties_present = (prop in data for prop in properties)
    errors_present = (len(errors[prop]) > 0 for prop in properties)

    if not all(properties_present) or any(errors_present):
        return

    temporal_start = parser.parse(data[('temporal_start',)])
    temporal_end = parser.parse(data[('temporal_end',)])

    [errors[prop].append('temporal_start cannot be greater or equal to temporal_end')
     for prop in properties if temporal_start >= temporal_end]

    return


def date_planned(key, data, errors, context):
    """
    When the `'dataset_status'` of a CKAN package is one of [`'http://data.overheid.nl/status/gepland'`,
    `'http://data.overheid.nl/status/in_onderzoek'`], then the `'date_planned'` property is required and must pass
    validation.

    No validation is performed whether or not the `'date_planned'` value makes 'sense'. It can be a value representing a
    point in time in the past, present or future.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    properties = [
        ('dataset_status',),
        ('date_planned',)
    ]
    errors_present = (len(errors[prop]) > 0 for prop in properties)
    affected_states = get_validation_configuration()['date_planned_states']

    if not properties[0] in data or any(errors_present):
        return key, data, errors, context

    try:
        data.get(properties[1])
    except KeyError:
        error_message = 'value is required when dataset_status is either [ {0} ]'.format(', '.join(affected_states))
        [errors[properties[1]].append(error_message) for data[properties[0]] in affected_states]

    return key, data, errors, context


def legal_foundation(key, data, errors, context):
    """
    Validates the `'legal_foundation_*'` values of the CKAN package. A legalFoundation is considered valid under the
    following conditions:
     - when any one of the `'legal_foundation_*'` properties is present, all other `'legal_foundation_*'` properties
       must also be present
     - all given `'legal_foundation_*'` properties which are present are also valid

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    properties = [
        ('legal_foundation_ref',),
        ('legal_foundation_uri',),
        ('legal_foundation_label',)
    ]
    properties_present = (prop in data for prop in properties)
    errors_present = (len(errors[prop]) > 0 for prop in properties)

    if not any(properties_present) or any(errors_present):
        return

    [errors[absentee].append('{0} is required when providing a legal_foundation'.format(absentee[0]))
     for absentee in [prop for prop in properties if prop not in data]]

    return


def checksum(key, data, errors, context):
    """
    Validates the `'checksum'` values of the CKAN package. A checksum is considered valid under the
    following conditions:
     - when either `hash` or `hash_algorithm` is present, the other must too be present
     - all given `'hash'` properties which are present are also valid

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    if ('resources', key[1], 'hash') in data and data[('resources', key[1], 'hash')] == '':
        data.pop(('resources', key[1], 'hash'), None)
        errors.pop(('resources', key[1], 'hash'), None)

    properties = [('resources', key[1], 'hash'), ('resources', key[1], 'hash_algorithm')]
    properties_present = (prop in data for prop in properties if prop)

    if not any(properties_present):
        return key, data, errors, context

    if not all(properties_present):
        for prop in properties:
            errors[prop].append('{0} is required when providing a valid checksum'.format(prop[2]))

    return key, data, errors, context


def rights(key, data, errors, context):
    """
    Validates the rights statements of the CKAN package. It states that when dataset_status is 'beschikbaar' and
    access_rights is 'PUBLIC' that an open license must be provided.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    dataset_status = data.get(('dataset_status',), None)
    access_rights = data.get(('access_rights',), None)
    license = data.get(('license_id',), None)

    status_is_available = dataset_status == 'http://data.overheid.nl/status/beschikbaar'
    access_rights_public = access_rights == 'http://publications.europa.eu/resource/authority/access-right/PUBLIC'
    license_is_open = license not in get_validation_configuration()['non_open_licenses']

    if status_is_available and access_rights_public and not license_is_open:
        errors[('license_id',)] = [
            'When dataset_status is set to [http://data.overheid.nl/status/beschikbaar] and '
            'access_rights is set to [http://publications.europa.eu/resource/authority/access-right/PUBLIC], '
            'an open license must be provided; got [{0}]'.format(license)
        ]

    return key, data, errors, context


def spatial(key, data, errors, context):
    """
    Validates that all the given `'spatial_values'` are validate according to their accompanied `'spatial_scheme'`.
    Since all `'spatial_value'`s are validated against such a `'spatial_scheme'` this means that both lists should be
    of the exact same size.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    properties = [('spatial_scheme',), ('spatial_value',)]
    properties_present = (prop in data for prop in properties)

    if not any(properties_present):
        return

    if any((len(errors[prop]) > 0 for prop in properties)):
        return

    if not all(properties_present):
        [errors[absentee].append('{0} is required when providing a spatial'.format(absentee[0]))
         for absentee in [prop for prop in properties if prop not in data]]

        return

    schemes = data[('spatial_scheme',)]
    values = data[('spatial_value',)]

    if len(schemes) != len(values):
        [errors[prop].append('the list of schemes must be of the same size as the list of values')
         for prop in properties]

        return

    validator_mapping = {
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.gemeente':
            tk.get_validator('controlled_vocabulary')('Overheid:SpatialGemeente'),
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.koninkrijksdeel':
            tk.get_validator('controlled_vocabulary')('Overheid:SpatialKoninkrijksdeel'),
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.provincie':
            tk.get_validator('controlled_vocabulary')('Overheid:SpatialProvincie'),
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.waterschap':
            tk.get_validator('controlled_vocabulary')('Overheid:SpatialWaterschap'),
        'http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.epsg28992':
            tk.get_validator('epsg_28992'),
        'http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.postcodehuisnummer':
            tk.get_validator('postcode_huisnummer')
    }

    error_message = 'spatial_value {0} is not valid according to scheme {1}'
    [errors[('spatial_value',)].append(error_message.format(val, schemes[iterator]))
     for iterator, val in enumerate(values) if not _valid_spatial(validator_mapping[schemes[iterator]], val)]

    return


def _valid_spatial(validation_method, value):
    """
    Executes a given validation method and returns whether or not any validation messages were generated.

    :param function validation_method: The validation method to execute
    :param any value:                  The value to validate

    :return: bool, Whether or not the value is valid
    """
    errors = {'value': []}
    validation_method('value', {'value': value}, errors, {})

    return len(errors['value']) == 0


def epsg28992(key, data, errors, context):
    """
    Validates that a given value is valid according to the EPSG:28992 coordinate reference system.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io
     - http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.epsg28992
     - https://epsg.io/28992

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    if key not in data:
        return

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        [errors[key].append('[{0}] is not a valid EPSG 28992 value'.format(val)) for val in data[key]
         if not re.match('^\d{6}(\.\d{3})? \d{6}(\.\d{3})?$', val)]

        return

    if not re.match('^\d{6}(\.\d{3})? \d{6}(\.\d{3})?$', data[key]):
        errors[key].append('[{0}] is not a valid EPSG 28992 value'.format(data[key]))

    return


def postcode_huisnummer(key, data, errors, context):
    """
    Validates that a given value is valid according to the Overheid:PostcodeHuisnummer reference system.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators
     - https://dcat-ap-donl.readthedocs.io
     - http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.postcodehuisnummer

    :param tuple key:    Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return: void
    """
    if key not in data:
        return

    errors[key] = [] if not errors[key] else errors[key]

    if isinstance(data[key], list):
        [errors[key].append(u'[{0}] is not a valid PostcodeHuisnummer value'.format(val)) for val in data[key]
         if not re.match('^[1-9]\d{3}([A-Z]{2}(\d+(\S+)?)?)?$', val)]

        return

    if not re.match('^[1-9]\d{3}([A-Z]{2}(\d+(\S+)?)?)?$', data[key]):
        errors[key].append(u'[{0}] is not a valid PostcodeHuisnummer value'.format(data[key]))

    return
