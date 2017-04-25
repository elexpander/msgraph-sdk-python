"""
Copyright (c) Microsoft Corporation.  All Rights Reserved.  Licensed under the MIT License.  See License in the project root for license information.
"""


class GraphObjectBase(object):

    def to_dict(self):
        """Returns the serialized form of the :class:`GraphObjectBase`
        as a dict. All sub-objects that are based off of :class:`GraphObjectBase`
        are also serialized and inserted into the dict
        
        Returns:
            dict: The serialized form of the :class:`GraphObjectBase`
        """
        serialized = {}

        for prop in self._prop_dict:
            if isinstance(self._prop_dict[prop], GraphObjectBase):
                serialized[prop] = self._prop_dict[prop].to_dict()
            else:
                serialized[prop] = self._prop_dict[prop]

        return serialized

    def __str__(self):
        """Returns a string representation of the object
        including object type and all properties
        
        Returns:
            string
        """
        output = '<MSGRAPH Object: ' + type(self).__name__ + ' {'
        serialized = self.to_dict()
        for key in serialized:
            if type(serialized[key]).__name__ == 'str':
                output = output + key + ': ' + serialized[key] + ', '
            else:
                output = output + key + ': <' + type(serialized[key]).__name__ + '>, '
        output = output + '}>'
        return output
