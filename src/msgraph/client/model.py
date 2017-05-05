"""
    Declare class factory
    Load clasess in dictonary (classname, class)
"""

from .metadata import *
from os.path import isfile
import json


class GraphObjectBase(object):

    def __str__(self):
        output = '<MSGRAPH Object: ' + type(self).__name__ + ' {\n'
        for k, v in self.__dict__.items():
            value = str(v)
            output += '\t' + k + ': ' + value + ',\n'
        output += '}'
        return output


class GraphModel(object):

    def __init__(self, model_file, base_url):
        """
        Loads classes from model file
        If model file doesn't exist, it generates it from the metadata.
        :param model_file: name of file with model in json format
        :param base_url: url of the metadata
        """

        if not isfile(model_file):
            # create model file from metadata
            metadata_dic = GraphMetadata(base_url)
            with open(model_file, 'w') as f:
                json.dump(metadata_dic, f)




        #load_classes()

    def get_class(self, name):
        return self.graph_classes[name]

    def _create_class(self,
                      name,
                      property_list,
                      navigation_property_list=None,
                      action_list=None,
                      function_list=None,
                      base_class=GraphObjectBase):

        def f__init__(self, properties):
            """
            Initialize instance of class
            :param self: 
            :param properties: dictionary with properties (name: value)
                               Properties may be other objects with their own properties
            :return: instance of class
            """
            if not base_class == GraphObjectBase:
                base_class.__init__(self, properties)

            for p_name, p_value in properties.items():
                if not p_name.startswith('@') and p_name in property_list:
                    setattr(self, p_name, p_value)

            """TypeError: Argument id not valid for GraphDirectoryRole
                hay que dar soporte de herencia
            """

        new_class = type(name, (base_class,), {"__init__": f__init__})
        return new_class


    def load_classes(self):
        """Return dictionary with all Graph Classes
        """
        for name, graph_type in self._graph_types.items():
            if isinstance(graph_type, GraphEntityType) and graph_type.base:
                base_class = GraphMetadata.graph_classes[graph_type.base]
                GraphMetadata.graph_classes[name] = self._create_class(name,
                                                                     property_list=list(graph_type.properties.keys()),
                                                                     base_class=base_class)
            else:
                GraphMetadata.graph_classes[name] = self._create_class(name,
                                                                     property_list=list(graph_type.properties.keys()))

