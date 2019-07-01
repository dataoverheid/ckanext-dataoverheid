# encoding: utf-8

"""
Provides method caching features.
"""


from datetime import datetime
import logging


logger = logging.getLogger('ckanext.dataoverheid')


_CACHED_DATE = int(datetime.strftime(datetime.now(), '%Y%m%d'))
_CACHE_STORE = {}


def cached(cached_function):
    """
    Provides a caching annotation for methods to use. The results of methods are cached for up to 24 hours. The first
    invocation of any given day will invalidate the cache and rebuild the cache based on a new actual execution of the
    method.

    :param cached_function: The method to perform the caching on
    :return: function, Returns a caching function
    """
    def function_wrapper(*args):
        """
        Performs caching on the results of a method invocation with the given arguments.

        :param args: The arguments given to the method
        :return: The cached result of the method invocation
        """
        global _CACHED_DATE, _CACHE_STORE
        _current_date = int(datetime.strftime(datetime.now(), '%Y%m%d'))

        if _current_date > _CACHED_DATE:
            logger.info(u'Cache expired; clearing...')

            _CACHE_STORE.clear()
            _CACHED_DATE = _current_date

        if (cached_function, args) in _CACHE_STORE:
            logger.info(u'Cache hit; {0} {1}'.format(cached_function, args))

            return _CACHE_STORE[(cached_function, args)]

        logger.info(u'Cache miss; {0} {1}'.format(cached_function, args))

        result = cached_function(*args)
        _CACHE_STORE[(cached_function, args)] = result

        return result

    return function_wrapper
