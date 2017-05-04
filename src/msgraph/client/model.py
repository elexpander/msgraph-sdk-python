"""
    Declare class factory
    Load clasess in dictonary (classname, class)
"""
import xml.etree.ElementTree as ET
from urllib.request import urlretrieve
from os.path import isfile


class GraphFunction(object):
    def __init__(self,
                 return_type=None,
                 parameters=None):
        super().__init__()
        self._return_type = return_type
        self._parameters = parameters


class GraphType(object):
    def __init__(self,
                 is_entity=False,
                 base_graph_type=None,
                 properties=None,
                 navigation_properties=None,
                 actions=None,
                 functions=None):
        super().__init__()
        self._is_entity = is_entity
        self._base_graph_type = base_graph_type
        self._properties = properties
        self._navigation_properties = navigation_properties
        self._actions = actions
        self._functions = functions

    @property
    def is_entity(self):
        """
        Gets is_entity
        :return: boolean
        """
        return self._is_entity

    @property
    def base(self):
        """
        Gets the base graph type
        :return: <string> base graph type
        """
        return self._base_graph_type

    @property
    def properties(self):
        """
        Gets properties
        :return: boolean
        """
        return self._properties

    def add_action(self, name, graph_action):
        """
        Adds a GraphFunction to the functions dictionary
        :param name: Name of function
        :param graph_action: GraphFunction object
        """
        if self._actions is None:
            self._actions = {name: graph_action}
        else:
            self._actions[name] = graph_action

    def add_function(self, name, graph_function):
        """
        Adds a GraphFunction to the functions dictionary
        :param name: Name of function
        :param graph_function: GraphFunction object
        """
        if self._functions is None:
            self._functions = {name: graph_function}
        else:
            self._functions[name] = graph_function


class GraphObjectBase(object):

    def __str__(self):
        output = '<MSGRAPH Object: ' + type(self).__name__ + ' {\n'
        for k, v in self.__dict__.items():
            value = str(v)
            output += '\t' + k + ': ' + value + ',\n'
        output += '}'
        return output


class GraphSchema(object):
    """
        graph_type {
            is_entity
            base
            properties: {
                graph_type
            }
            navigation_properties: {
                graph_type
            }
            graph_actions: {
                return_graph_type
                parameters {
                    graph_type
                }
            }
            graph_functions: {
                return_graph_type
                parameters {
                    graph_type
                }
            }
        }
    """
    graph_classes = {}

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
        schema = next(root.iter(self._add_ns_to_tag('Schema')))

        # Load namespace prefix, normally microsoft.graph.
        self._ns_prefix = schema.attrib['Namespace'] + '.'

        # EnumType to Dictionary - https://docs.python.org/3/library/enum.html
        for e_type in schema.iterfind(self._add_ns_to_tag('EnumType')):
            d_type = {}
            for e_attrib in e_type.iterfind(self._add_ns_to_tag('Member')):
                # Add attribute to type dictionary
                d_type[e_attrib.attrib['Value']] = e_attrib.attrib['Name']

            # Add type to schema dictionary
            self._graph_enums[GraphSchema.get_python_tag(e_type.attrib['Name'])] = d_type

        # Process EntityType
        for e_type in schema.iterfind(self._add_ns_to_tag('EntityType')):

            # Get type name
            type_name = GraphSchema.get_python_tag(e_type.attrib['Name'])

            # Get type properties
            properties = {}
            for e_attrib in e_type.iterfind(self._add_ns_to_tag('Property')):
                # Add attribute to type dictionary
                properties[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            # Load entity navigation_properties
            navigation_properties = {}
            for e_attrib in e_type.iterfind(self._add_ns_to_tag('NavigationProperty')):
                # Add attribute to type dictionary
                navigation_properties[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            # Get entity base entity
            if 'BaseType' in e_type.attrib:
                base = GraphSchema.get_python_tag(e_type.attrib['BaseType'])
            else:
                base = None

            # Create entity_type dictionary object
            entity_type = GraphType(is_entity=True,
                                    base_graph_type=base,
                                    properties=properties,
                                    navigation_properties=navigation_properties,
                                    functions={})

            # Add entity_type to graph_type dictionary
            self._graph_types[type_name] = entity_type

        # Process ComplexType
        for e_type in schema.iterfind(self._add_ns_to_tag('ComplexType')):

            # Get type name
            type_name = GraphSchema.get_python_tag(e_type.attrib['Name'])

            # Get type properties
            properties = {}
            for e_attrib in e_type.iterfind(self._add_ns_to_tag('Property')):
                # Add attribute to type dictionary
                properties[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            complex_type = GraphType(properties=properties)

            # Add type to schema dictionary
            self._graph_types[type_name] = complex_type

        # Process Actions
        for e_type in schema.iterfind(self._add_ns_to_tag('Action')):
            parameters = {}
            binding = None

            for e_attrib in e_type.iterfind(self._add_ns_to_tag('Parameter')):
                if e_attrib.attrib['Name'] == 'bindingParameter':
                    binding = GraphSchema.get_python_tag(e_attrib.attrib['Type'])
                else:
                    # Add attribute type to parameters dictionary
                    parameters[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            if binding:
                # Load return_graph_type
                try:
                    et_return_type = next(e_type.iterfind(self._add_ns_to_tag('ReturnType')))
                    return_type = et_return_type.attrib['Type']
                except:
                    return_type = None

                type_function = GraphFunction(return_type=return_type,
                                              parameters=parameters)

                # Attach action to entity_type in graph_type dictionary
                self._graph_types[binding].add_action(e_type.attrib['Name'], type_function)

        # Process Functions
        for e_type in schema.iterfind(self._add_ns_to_tag('Function')):
            parameters = {}
            binding = None

            for e_attrib in e_type.iterfind(self._add_ns_to_tag('Parameter')):
                if e_attrib.attrib['Name'] == 'bindingParameter':
                    binding = GraphSchema.get_python_tag(e_attrib.attrib['Type'])
                else:
                    # Add attribute type to parameters dictionary
                    parameters[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            if binding:
                # Load return_graph_type
                try:
                    et_return_type = next(e_type.iterfind(self._add_ns_to_tag('ReturnType')))
                    return_type = et_return_type.attrib['Type']
                except:
                    return_type = None
                type_function = GraphFunction(return_type=return_type,
                                              parameters=parameters)

                # Attach action to entity_type in graph_type dictionary
                self._graph_types[binding].add_function(e_type.attrib['Name'], type_function)

    def _add_ns_to_tag(self, tag):
        """Return tag with full namespace format
        """
        return self._ns + tag.replace(self._ns_prefix, '')

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
            # Remove /$entity tag from context if it was there
            new_tag = context.replace('/$entity', '')

            # Remove the plural 's'
            new_tag = new_tag.rstrip('s')

        else:
            raise ValueError('No value received.')

        return 'Graph' + new_tag[0].upper() + new_tag[1:]

    def load_classes(self):
        """Return dictionary with all Graph Classes
        """
        for name, graph_type in self._graph_types.items():
            if graph_type.base:
                base_class = GraphSchema.graph_classes[graph_type.base]
                GraphSchema.graph_classes[name] = self._create_class(name,
                                                                     property_list=list(graph_type.properties.keys()),
                                                                     base_class=base_class)
            else:
                GraphSchema.graph_classes[name] = self._create_class(name,
                                                                     property_list=list(graph_type.properties.keys()))

    @staticmethod
    def get_class(name):
        return GraphSchema.graph_classes[name]

    def _create_class(self,
                      name,
                      property_list,
                      navigation_property_list=None,
                      action_list=None,
                      function_list=None,
                      base_class=GraphObjectBase):

        def f__init__(self, args):
            if not base_class == GraphObjectBase:
                base_class.__init__(self, args)

            for p_name, p_value in args.items():
                if not p_name.startswith('@') and p_name in property_list:
                    setattr(self, p_name, p_value)

            """TypeError: Argument id not valid for GraphDirectoryRole
                hay que dar soporte de herencia
            """

        new_class = type(name, (base_class,), {"__init__": f__init__})
        return new_class



