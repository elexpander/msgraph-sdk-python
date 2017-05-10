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

    graph_classes = {}

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
                json.dump(metadata_dic, f, indent=4)



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


    @staticmethod
    def get_python_tag(tag, context=None):
        """Return tag with Python Class format (GraphClassName)
        """
        if tag:
            pos = tag.find('}')
            if pos > 0:
                # tag is in namespace format
                new_tag = tag[pos+1:]

            elif len(tag.split('.')) == 3:
                # tag is in microsoft.graph format
                new_tag = tag.split('.')[-1]

            else:
                new_tag = tag

        elif context:

            if '$entity' in context:
                # Remove /$entity tag from context if it was there
                new_tag = context.replace('/$entity', '')

            elif '/' in context:
                new_tag = context.split('/')[-1]

            # Remove the plural 's'
            new_tag = new_tag.rstrip('s')

        else:
            raise ValueError('No value received.')

        return 'Graph' + new_tag[0].upper() + new_tag[1:]