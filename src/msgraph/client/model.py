"""
    Declare class factory
    Load clasess in dictonary (classname, class)
"""
import xml.etree.ElementTree as ET
from urllib.request import urlretrieve
from os.path import isfile


class GraphFunction(object):
    def __init__(self,
                 is_action=False,
                 return_type=None,
                 parameters=None):
        super().__init__()
        self._is_action = is_action
        self._return_type = return_type
        self._parameters = parameters


class GraphType(object):
    def __init__(self,
                 is_entity=False,
                 base_graph_type=None,
                 properties=None,
                 navigation_properties=None,
                 functions=None):
        super().__init__()
        self._is_entity = is_entity
        self._base_graph_type = base_graph_type
        self._properties = properties
        self._navigation_properties = navigation_properties
        self._functions = functions

    @property
    def is_entity(self):
        """
        Gets is_entity
        :return: boolean
        """
        return self._is_entity

    @property
    def properties(self):
        """
        Gets properties
        :return: boolean
        """
        return self._properties

    def add_function(self, name, graph_function):
        """
        Adds a GraphFunction to the functions dictionary
        :param name: Name of function
        :param graph_function: GraphFunction object
        """
        self._functions[name] = graph_function


class GraphObjectBase(object):

    def __str__(self):
        output = '<MSGRAPH Object: ' + type(self).__name__ + ' {\n'
        for k, v in self.__dict__.items():
            output += '\t' + k + ': ' + v + ',\n'
        output += '}'
        return output


class GraphSchema(object):
    """
        graph_type {
            is_entity
            base_graph_type
            properties: {
                graph_type
            }
            navigation_properties: {
                graph_type
            }
            graph_functions {
                is_action
                return_graph_type
                parameters {
                    graph_type
                }
            }
        }
    """
    def __init__(self, base_url):
        self._schema_file = 'schema.xml'
        self._ns = '{http://docs.oasis-open.org/odata/ns/edm}'
        self._ns_prefix = ''

        self._graph_enums = {}
        self._graph_types = {}

        if not isfile(self._schema_file):
            # Download file
            urlretrieve(base_url + '/$metadata', self._schema_file)

        # Load schema XML file
        tree = ET.parse(self._schema_file)
        root = tree.getroot()
        schema = next(root.iter(self._ns_tag('Schema')))

        # Load namespace prefix, normally microsoft.graph.
        self._ns_prefix = schema.attrib['Namespace'] + '.'

        # EnumType to Dictionary - https://docs.python.org/3/library/enum.html
        for e_type in schema.iterfind(self._ns_tag('EnumType')):
            d_type = {}
            for e_attrib in e_type.iterfind(self._ns_tag('Member')):
                # Add attribute to type dictionary
                d_type[e_attrib.attrib['Value']] = e_attrib.attrib['Name']

            # Add type to schema dictionary
            self._graph_enums[self._graph_tag(e_type.attrib['Name'])] = d_type

        # Process EntityType
        for e_type in schema.iterfind(self._ns_tag('EntityType')):

            # Load entity properties
            properties = {}
            for e_attrib in e_type.iterfind(self._ns_tag('Property')):
                # Add attribute to type dictionary
                properties[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            # Load entity navigation_properties
            navigation_properties = {}
            for e_attrib in e_type.iterfind(self._ns_tag('NavigationProperty')):
                # Add attribute to type dictionary
                navigation_properties[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            # Create entity_type dictionary object
            base = e_type.attrib['BaseType'] if 'BaseType' in e_type.attrib else None
            entity_type = GraphType(is_entity=True,
                                    base_graph_type=base,
                                    properties=properties,
                                    navigation_properties=navigation_properties,
                                    functions={})

            # Add entity_type to graph_type dictionary
            self._graph_types[self._class_tag(e_type.attrib['Name'])] = entity_type

        # Process ComplexType
        for e_type in schema.iterfind(self._ns_tag('ComplexType')):
            properties = {}
            for e_attrib in e_type.iterfind(self._ns_tag('Property')):
                # Add attribute to type dictionary
                properties[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            complex_type = GraphType(properties=properties)

            # Add type to schema dictionary
            self._graph_types[self._class_tag(e_type.attrib['Name'])] = complex_type

        # Process Actions
        for e_type in schema.iterfind(self._ns_tag('Action')):
            parameters = {}
            binding = None

            for e_attrib in e_type.iterfind(self._ns_tag('Parameter')):
                if e_attrib.attrib['Name'] == 'bindingParameter':
                    binding = e_attrib.attrib['Type']
                else:
                    # Add attribute type to parameters dictionary
                    parameters[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            if binding:
                # Load return_graph_type
                try:
                    et_return_type = next(e_type.iterfind(self._ns_tag('ReturnType')))
                    return_type = et_return_type.attrib['Type']
                except:
                    return_type = None

                type_function = GraphFunction(is_action=True,
                                              return_type=return_type,
                                              parameters=parameters)

                # Attach action to entity_type in graph_type dictionary
                self._graph_types[self._class_tag(binding)].add_function(e_type.attrib['Name'], type_function)

        # Process Functions
        for e_type in schema.iterfind(self._ns_tag('Function')):
            parameters = {}
            binding = None

            for e_attrib in e_type.iterfind(self._ns_tag('Parameter')):
                if e_attrib.attrib['Name'] == 'bindingParameter':
                    binding = e_attrib.attrib['Type']
                else:
                    # Add attribute type to parameters dictionary
                    parameters[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            if binding:
                # Load return_graph_type
                try:
                    et_return_type = next(e_type.iterfind(self._ns_tag('ReturnType')))
                    return_type = et_return_type.attrib['Type']
                except:
                    return_type = None
                type_function = GraphFunction(is_action=False,
                                              return_type=return_type,
                                              parameters=parameters)

                # Attach action to entity_type in graph_type dictionary
                self._graph_types[self._class_tag(binding)].add_function(e_type.attrib['Name'], type_function)

    def _ns_tag(self, tag):
        """Return tag with full namespace format
        """
        return self._ns + tag.replace(self._ns_prefix, '')

    def _graph_tag(self, tag):
        """Return tag with api type format. Normally microsoft.graph.tag
        """
        return self._ns_prefix + tag.replace(self._ns, '')

    def _class_tag(self, tag):
        """Return tag with Python Class format (GraphClassName)
        """
        new_tag = tag.replace(self._ns, '').replace(self._ns_prefix, '')
        return 'Graph' + new_tag[0].upper() + new_tag[1:]

    def load_classes(self):
        """Return dictionary with all Graph Classes
        """
        graph_class = {}

        for name, graph_type in self._graph_types.items():
            graph_class[name] = self._create_class(name, list(graph_type.properties.keys()))

        return graph_class

    def _create_class(self, name, argnames, base_class=GraphObjectBase):
        def f__init__(self, **kwargs):
            for key, value in kwargs.items():
                # argnames variable is the one passed to _create_class
                if key not in argnames:
                    raise TypeError("Argument %s not valid for %s"
                        % (key, self.__class__.__name__))
                setattr(self, key, value)
                base_class.__init__(self)
        new_class = type(name, (base_class,), {"__init__": f__init__})
        return new_class



