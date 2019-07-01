# encoding: utf-8

import json
import urllib2
from ckanext.dataoverheid.helper import cached, get_taxonomies


def in_taxonomy(name):
    def taxonomy_validator(key, data, errors, context):
        taxonomy = _load_taxonomy(name)
        input_values = data.get(key, None)

        errors[key] = [] if not errors[key] else errors[key]

        if not input_values:
            return key, data, errors, context

        if isinstance(input_values, list):
            for input_value in input_values:
                if input_value not in taxonomy:
                    errors[key].append(u'value [{0}] is not part of taxonomy [{1}]'.format(input_values, name))

            return key, data, errors, context

        if input_values not in taxonomy:
            errors[key].append(u'value [{0}] is not part of taxonomy [{1}]'.format(input_values, name))

        return key, data, errors, context

    return taxonomy_validator


@cached
def _load_taxonomy(name):
    try:
        taxonomy = get_taxonomies()[name]
        taxonomy_contents = urllib2.urlopen(taxonomy['online'])
        json_taxonomy_contents = json.loads(taxonomy_contents.read())
        keys = []

        for entry in json_taxonomy_contents:
            keys.append(entry['field_identifier'])

        return keys
    except KeyError:
        raise Exception(u'the requested taxonomy [{0}] does not exist or is not supported'.format(name))
