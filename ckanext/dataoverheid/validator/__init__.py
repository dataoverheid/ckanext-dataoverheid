# encoding: utf-8

"""
Exposes validator methods that perform validations on specified keys in dictionaries.
"""

import type_validator
import controlled_vocabulary
import multi_property_validator
import spatial_validator
import taxonomy_validator
import determine_communities


_VALIDATORS = {
    'single_value':                 type_validator.single_valued,
    'multi_value':                  type_validator.multi_valued,
    'is_string':                    type_validator.string,
    'is_bool':                      type_validator.boolean,
    'is_uri':                       type_validator.uri,
    'is_date':                      type_validator.date,
    'is_number':                    type_validator.number,
    'controlled_vocabulary':        controlled_vocabulary.in_taxonomy,
    'taxonomy':                     taxonomy_validator.in_taxonomy,
    'multi_field_validation':       multi_property_validator.multi_field_validation,
    'res_multi_field_validation':   multi_property_validator.res_multi_field_validation,
    'valid_epsg28992':              spatial_validator.valid_epsg28992,
    'valid_postcode_huisnummer':    spatial_validator.valid_postcode_huisnummer,
    'determine_communities':        determine_communities.extract_communities
}


def get_all():
    """
    Get and return all the defined validator methods.

    :return: dict, A dictionary containing all the validator methods
    """
    return _VALIDATORS
