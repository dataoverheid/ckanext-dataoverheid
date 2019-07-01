# encoding: utf-8

"""
Exposes functionality that allows default values to be set for fields in the package dictionary.
"""


def default(default_value, force=False):
    """
    Creates a function which allows a field to fallback to a given default value.

    :param default_value: The default value to set
    :param force: Whether or not to force the default value regardless of a value already being present
    :return: function
    """
    def default_setter(value):
        """
        Sets the value to the given default value, assuming the original value is not set or the default value is set to
        forced.

        :param value: The original value
        :return: The original, possibly modified, value
        """
        return value if value and not force else default_value

    return default_setter
