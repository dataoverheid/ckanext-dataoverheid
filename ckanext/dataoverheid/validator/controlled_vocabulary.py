# encoding: utf-8

"""
Exposes validation functionality allowing values to be checked against controlled vocabularies.
"""

import os
import json
from ckanext.dataoverheid.helper import cached, get_controlled_vocabularies


def in_taxonomy(name):
    """
    Exposes a validation method which checks if a given value is present in the controlled vocabulary matching the name
    argument.

    :param name: string, The name of the controlled vocabulary
    :return: function, The validation function
    """
    def taxonomy_validator(key, data, errors, context):
        """
        Validates if the value behind the key in the data dictionary is present in the controlled vocabulary. If a list
        of values is given then the all the items in the list are checked against the vocabulary.

        :param key: tuple, The key to check
        :param data: dict, The dictionary containing the key
        :param errors: dict, The error dictionary matching the data dictionary
        :param context: dict, The current CKAN context
        :return: The original, possibly modified, arguments as a tuple
        """
        taxonomy = _get_taxonomy(name)
        input_values = data.get(key, None)

        errors[key] = [] if not errors[key] else errors[key]

        if not input_values:
            return key, data, errors, context

        if isinstance(input_values, list):
            for input_value in input_values:
                if input_value not in taxonomy:
                    errors[key].append(u'value [{0}] is not part of taxonomy [{1}]'.format(input_value, name))

            return key, data, errors, context

        if input_values not in taxonomy:
            errors[key].append(u'value [{0}] is not part of taxonomy [{1}]'.format(input_values, name))

        return key, data, errors, context

    return taxonomy_validator


@cached
def _get_taxonomy(name):
    """
    Loads the contents of the given controlled vocabulary. The results of this method invocation are cached for up to
    24 hours.

    :param name: string, The name of the controlled vocabulary
    :return: list, The contents of the controlled vocabulary
    """
    try:
        filepath = os.path.join(os.path.dirname(__file__), '..', 'resources', 'controlled_vocabularies',
                                get_controlled_vocabularies()[name]['local'])

        with open(filepath, 'rb') as file_contents:
            parsed = json.loads(file_contents.read())

            try:
                if name == u'Overheid:License':
                    keys = []

                    for block in parsed:
                        if 'id' in block:
                            keys.append(block['id'])

                    return keys

                return parsed.keys()
            except KeyError:
                raise Exception(u'{0} is malformed;'.format(name))
    except KeyError:
        raise Exception(u'the requested controlled vocabulary [{0}] does not exist or is not supported'.format(name))
