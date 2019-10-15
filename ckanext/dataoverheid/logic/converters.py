# encoding: utf-8


def convert_string_to_list(key, data, errors, context):
    """
    If the value behind `'data.get(key)'` is present, it will be converted to a list under the following conditions:
     - The value is of type string
     - The value starts with the character `'{'`
     - The value ends with the character `'}'`

    If any of the conditions are not met, no action will be taken.

    This converter is necessary because for some reason when lists are send to and from CKAN / Solr they get transformed
    into string surrounded by {} characters.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators

    :param str  key:     Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return void
    """
    value = data.get(key, None)

    if not value or not isinstance(value, basestring) or not value.startswith('{') or not value.endswith('}'):
        return

    value = value.replace('"', '')
    data[key] = value[1:len(value)-1].split(',')


def convert_list_to_string(key, data, errors, context):
    """
    If the value behind `'data.get(key)` is present, it will be converted to a string under the following conditions:
     - The value is type list

    If any of the conditions are not met, no action will be taken.

    The resulting string will be surrounded by `'{}'`. The entries in the list will be separated by a `','` in the
    resulting string.

    This converter is necessary because for some reason when lists are send to and from CKAN / Solr they get transformed
    into string surrounded by {} characters.

    See also:
     - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators

    :param str  key:     Injected by CKAN core
    :param dict data:    Injected by CKAN core
    :param dict errors:  Injected by CKAN core
    :param dict context: Injected by CKAN core

    :return void
    """
    value = data.get(key, None)

    if not value or not isinstance(value, list):
        return

    data[key] = '{{0}}'.format(','.join(map(str, value)))


def default(default_value, force=False):
    """
    Creates a function which allows a field to fallback to a given default value.

    :param any default_value: The default value to set
    :param bool force: Whether or not to force the default value regardless of a value already being present

    :return: func, The created validation function
    """
    def default_setter(value):
        """
        Sets the value to the given default value, assuming the original value is not set or the default value is set to
        forced.

        See also:
         - https://docs.ckan.org/en/latest/extensions/adding-custom-fields.html#custom-validators

        :param any value: Injected by CKAN core

        :return: any, The original, possibly modified, value
        """
        return value if value and not force else default_value

    return default_setter
