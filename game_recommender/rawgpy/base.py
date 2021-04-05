"""The base class for converting from JSON
"""
from . import utils
import inspect
import traceback
from . import rawg


class FromJSONobject():
    """a base object that provides functionality for converting from json
    """

    def __init__(self, json):
        self._raw_json = json
        self.json = utils.del_none(json)
        self.rawg = rawg.RAWG()
        for key in self.json.keys():
            # iterate over all keys in json
            hname = "_{}".format(key)
            # formate the hname with a underscore in front
            setattr(self, hname, json[key])
            # set the hidden attribute that the property corresponds to
            setattr(FromJSONobject, key, property(
                self._create_getter(hname), self._create_setter(hname)))
            # set the property, usign the create_getter and create_setter methods to get the specific getter / setter method

    def _create_getter(self, attrname):
        # creates the getter function for attrname
        def getter_template(self):
            # returns the getattr result for attrname
            return getattr(self, attrname)
        return getter_template  # returning the function object without calling it, by doing this we save the current state of the function, together with the current attrname

    def _create_setter(self, attrname):  # the same as _create_getter, just using setattr
        def setter_template(self, value):
            return setattr(self, attrname, value)
        return setter_template
