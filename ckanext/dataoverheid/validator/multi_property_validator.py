# encoding: utf-8

"""
Exposes validation methods which span over multiple fields of a CKAN package or resource.
"""

import dateutil.parser as parser
import ckan.plugins.toolkit as tk
from ckanext.dataoverheid.helper import get_non_open_licenses


def multi_field_validation(key, data, errors, context):
    """
    Applies all the multi-field validation methods to the given package.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    key, data, errors, context = contact_point_validation(key, data, errors, context)
    key, data, errors, context = temporal_validation(key, data, errors, context)
    key, data, errors, context = date_planned_validation(key, data, errors, context)
    key, data, errors, context = legal_foundation_validation(key, data, errors, context)
    key, data, errors, context = spatial_validation(key, data, errors, context)
    key, data, errors, context = rights_validation(key, data, errors, context)

    return key, data, errors, context


def res_multi_field_validation(key, data, errors, context):
    """
    Applies all the multi-field validation methods to the given resource.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the resource
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    key, data, errors, context = hash_validation(key, data, errors, context)

    return key, data, errors, context


def contact_point_validation(key, data, errors, context):
    """
    Validates the contact_point_* values of the CKAN package. It states that either contact_point_website,
    contact_point_email or contact_point_phone must be present in order for a contact_point to be valid.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    properties = [
        ('contact_point_website',),
        ('contact_point_email',),
        ('contact_point_phone',)
    ]
    properties_present = (prop in data for prop in properties)
    error_message = u'website, email or phone is required for a valid contact_point'

    if not any(properties_present):
        for prop in properties:
            errors[prop].append(error_message)

    return key, data, errors, context


def temporal_validation(key, data, errors, context):
    """
    Validates the temporal_* values of the CKAN package. It states that if both temporal_start and temporal_end are
    present that the datetime value of temporal_start must occur before the datetime value of temporal_end.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    properties = [
        ('temporal_start',),
        ('temporal_end',)
    ]
    properties_present = (prop in data for prop in properties)
    errors_present = (len(errors[prop]) > 0 for prop in properties)

    if not all(properties_present):
        return key, data, errors, context

    if any(errors_present):
        return key, data, errors, context

    temporal_start = parser.parse(data[('temporal_start',)])
    temporal_end = parser.parse(data[('temporal_end',)])

    if temporal_start >= temporal_end:
        for prop in properties:
            errors[prop].append(u'temporal_start cannot be greater or equal to temporal_end')

    return key, data, errors, context


def date_planned_validation(key, data, errors, context):
    """
    Validates the date_planned value of the CKAN package. It states that when the dataset_status value of the package
    is either 'gepland' or 'in_onderzoek' that the date_planned field is mandatory.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    dataset_status_tuple = ('dataset_status',)
    affected_states = ['http://data.overheid.nl/status/gepland', 'http://data.overheid.nl/status/in_onderzoek']
    affected_states_str = u', '.join(affected_states)

    if dataset_status_tuple not in data:
        return key, data, errors, context

    if data[dataset_status_tuple] in affected_states:
        if not ('date_planned',) in data:
            errors[('date_planned',)] = [
                u'value is required when dataset_status is in [ {0} ]'.format(affected_states_str)
            ]

    return key, data, errors, context


def legal_foundation_validation(key, data, errors, context):
    """
    Validates the legal_foundation_* values of the CKAN package. It states that when one of the legal_foundation_*
    properties is present, they all must be present.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    properties = [
        ('legal_foundation_ref',),
        ('legal_foundation_uri',),
        ('legal_foundation_label',)
    ]
    properties_present = (prop in data for prop in properties)
    errors_present = (len(errors[prop]) > 0 for prop in properties)

    if not any(properties_present):
        return key, data, errors, context

    if any(errors_present):
        return key, data, errors, context

    absentees = (prop for prop in properties if prop not in data)

    for absentee in absentees:
        if not errors[absentee]:
            errors[absentee] = []

        errors[absentee].append(u'{0} is required when providing a legal_foundation'.format(absentee[0]))

    return key, data, errors, context


def hash_validation(key, data, errors, context):
    """
    Validates the hash values of the CKAN resource. It states that when either a hash or a hash_algorithm is provided,
    the other (hash or hash_algorithm) must too be provided.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
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
            errors[prop].append(u'{0} is required when providing a valid checksum'.format(prop[2]))

    return key, data, errors, context


def spatial_validation(key, data, errors, context):
    """
    Validates the spatial_schemes and spatial_values of the CKAN package. It states that the values of spatial_value
    must be validates against the schemes provided in spatial_scheme.

    This means that the list fo spatial_scheme must be of the same size as spatial_value.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    properties = [('spatial_scheme',), ('spatial_value',)]
    properties_present = (prop in data for prop in properties)
    errors_present = (len(errors[prop]) > 0 for prop in properties)

    if not any(properties_present):
        return key, data, errors, context

    if any(errors_present):
        return key, data, errors, context

    if not all(properties_present):
        absentees = (prop for prop in properties if prop not in data)

        for absentee in absentees:
            if not errors[absentee]:
                errors[absentee] = []

            errors[absentee].append(u'{0} is required when providing a spatial'.format(absentee[0]))

        return key, data, errors, context

    schemes = data[('spatial_scheme',)]
    values = data[('spatial_value',)]

    if len(schemes) != len(values):
        for prop in properties:
            errors[prop].append(u'the list of schemes must be of the same size as the list of values')

        return key, data, errors, context

    validator_mapping = {
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.gemeente':                  tk.get_validator('controlled_vocabulary')('Overheid:SpatialGemeente'),
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.koninkrijksdeel':           tk.get_validator('controlled_vocabulary')('Overheid:SpatialKoninkrijksdeel'),
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.provincie':                 tk.get_validator('controlled_vocabulary')('Overheid:SpatialProvincie'),
        'http://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.waterschap':                tk.get_validator('controlled_vocabulary')('Overheid:SpatialWaterschap'),
        'http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.epsg28992':          tk.get_validator('valid_epsg28992'),
        'http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.postcodehuisnummer': tk.get_validator('valid_postcode_huisnummer')
    }

    for iterator, val in enumerate(values):
        if not _valid_spatial(validator_mapping[schemes[iterator]], val):
            errors[('spatial_value',)].append(u'spatial_value {0} is not valid according to scheme {1}'.format(val, schemes[iterator]))

    return key, data, errors, context


def rights_validation(key, data, errors, context):
    """
    Validates the rights statements of the CKAN package. It states that when dataset_status is 'beschikbaar' and
    access_rights is 'PUBLIC' that an open license must be provided.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    dataset_status = data.get(('dataset_status',), None)
    access_rights = data.get(('access_rights',), None)
    license = data.get(('license_id',), None)

    status_is_available = dataset_status == u'http://data.overheid.nl/status/beschikbaar'
    access_rights_public = access_rights == u'http://publications.europa.eu/resource/authority/access-right/PUBLIC'
    license_is_open = license not in get_non_open_licenses()

    if status_is_available and access_rights_public and not license_is_open:
        errors[('license_id',)] = [
            u'When dataset_status is set to [http://data.overheid.nl/status/beschikbaar] and '
            u'access_rights is set to [http://publications.europa.eu/resource/authority/access-right/PUBLIC], '
            u'an open license must be provided; got [{0}]'.format(license)
        ]

    return key, data, errors, context


def _valid_spatial(validation_method, value):
    """
    Validates a given spatial_value value against the spatial_scheme validator.

    :param key: tuple, The key, not used
    :param data: dict, The data dictionary representing the package
    :param errors: dict, The validation errors so far
    :param context: dict, The current CKAN context
    :return: The original, possibly modified, arguments
    """
    key, data, errors, context = validation_method('value', {'value': value}, {'value': []}, {})

    return len(errors['value']) == 0
