"""Utility functions and classes
"""
def del_none(obj):
    """recursive function for deleting none from json-dict

    recursively removes none from a nested python data structure (dict, tuple, list, thing)

    :param obj: the object none values are to be removed from
    :type obj: dict, list, set, tuple
    :return: the object without none values
    :rtype: dict, list, set, tuple
    """
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(del_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)((del_none(k), del_none(v))
                         for k, v in obj.items() if k is not None and v is not None)
    else:
        return obj

# code from https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
