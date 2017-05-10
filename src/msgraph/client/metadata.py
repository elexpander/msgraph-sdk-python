import xml.etree.ElementTree as ET
from urllib.request import urlretrieve
from os.path import isfile


class GraphFunction(dict):
    def __init__(self,
                 returns=None,
                 parameters=None):
        super().__init__()
        self['returns'] = returns
        self['parameters'] = parameters


class GraphComplexType(dict):
    def __init__(self, properties=None):
        super().__init__()
        self['properties'] = properties

    @property
    def properties(self):
        """
        Gets properties
        :return: boolean
        """
        return self['properties']


class GraphEntityType(GraphComplexType):
    """
        graph_type {
            name
            base
            attributes: {
                name
                type
            }
            navigation_attributes: {
                name
                type
            }
            actions: { - POST request with parameters in body
                name
                return_type
                parameters {
                    name
                    type
                }
            }
            functions: { - GET request with parameters in url: reminderView(startDateTime=startDateTime-value,endDateTime=endDateTime-value)
                name
                return_type
                parameters {
                    name
                    type
                }
            }
        }
    """

    def __init__(self,
                 base_graph_type=None,
                 properties=None,
                 navigation_properties=None,
                 actions=None,
                 functions=None):
        super().__init__(properties)
        self['base'] = base_graph_type
        self['navigation_properties'] = navigation_properties
        self['actions'] = actions
        self['functions'] = functions

    @property
    def base(self):
        """
        Gets the base graph type
        :return: <string> base graph type
        """
        return self['base_graph_type']

    def add_action(self, name, graph_action):
        """
        Adds a GraphFunction to the functions dictionary
        :param name: Name of function
        :param graph_action: GraphFunction object
        """
        if self['actions'] is None:
            self['actions'] = {name: graph_action}
        else:
            self['actions'].update({name: graph_action})

    def add_function(self, name, graph_function):
        """
        Adds a GraphFunction to the functions dictionary
        :param name: Name of function
        :param graph_function: GraphFunction object
        """
        if self['functions'] is None:
            self['functions'] = {name: graph_function}
        else:
            self['functions'].update({name: graph_function})


class GraphMetadata(dict):

    def __init__(self, base_url):
        super().__init__()

        # variables
        self._metadata_file = 'metadata.xml'
        self._ns = '{http://docs.oasis-open.org/odata/ns/edm}'
        self._ns_prefix = ''
        self._graph_enums = {}
        self._graph_calls = {}

        # functions
        def add_ns_to_tag(tag):
            """Return tag with full namespace format
            """
            return self._ns + tag
        
        def pythonize_type(name):
            """
            Convert name into python class format
            :param name: string with name in odata format
            :return: string with name in ThisFormat
            """
            edm_to_python = {'Edm.String': 'string',
                             'Edm.SByte': 'int',
                             'Edm.Int16': 'int',
                             'Edm.Int32': 'int',
                             'Edm.Int64': 'int',
                             'Edm.Decimal': 'float',
                             'Edm.Single': 'float',
                             'Edm.Double': 'float',
                             'Edm.Boolean': 'bool',
                             'Edm.TimeOfDay': 'string',
                             'Edm.Date': 'datetime',
                             'Edm.DateTimeOffset': 'datetime',
                             'Edm.Duration': 'timedelta',
                             'Edm.Guid': 'string',
                             'Edm.Stream': 'bytes',
                             'Edm.Binary': 'bytes'}

            if name.startswith('Collection('):
                # remove Collection from name
                name = name[11:-1]
                is_list = True
            else:
                is_list = False

            if name.startswith('microsoft.graph.'):
                name = name.split('.')[-1]
                name = 'Graph' + name[0].upper() + name[1:]

            elif name.startswith('Edm.'):
                # convert edm type to python
                name = edm_to_python[name]
            else:
                name = 'Graph' + name[0].upper() + name[1:]

            if is_list:
                name = '*' + name
            return name

        def pythonize_attribute(name):
            """
            Convert name into python attribute format
            :param name: string with name in thisFormat
            :return: string with name in this_format
            """
            return ''.join(["_" + c.lower() if c.isupper() else c for c in name])

        # begining of _init_
        if not isfile(self._metadata_file):
            # Download file
            urlretrieve(base_url + '/$metadata', self._metadata_file)

        # Load schema XML file
        tree = ET.parse(self._metadata_file)
        root = tree.getroot()
        schema = next(root.iter(add_ns_to_tag('Schema')))

        # Load namespace prefix, normally microsoft.graph.
        self._ns_prefix = schema.attrib['Namespace'] + '.'

        # Process EnumType - https://docs.python.org/3/library/enum.html
        for e_type in schema.iterfind(add_ns_to_tag('EnumType')):
            d_type = {}
            for e_attrib in e_type.iterfind(add_ns_to_tag('Member')):
                # Add attribute to type dictionary
                d_type[e_attrib.attrib['Value']] = e_attrib.attrib['Name']

            # Add type to schema dictionary
            self._graph_enums[pythonize_type(e_type.attrib['Name'])] = d_type

        # Process EntityContainer (name: type)
        for e_type in schema.iterfind(add_ns_to_tag('EntityContainer')):
            d_type = {}
            for e_attrib in e_type.iterfind(add_ns_to_tag('EntitySet')):
                # Add EntitySet to dictionary
                d_type[e_attrib.attrib['Name']] = e_attrib.attrib['EntityType']

            for e_attrib in e_type.iterfind(add_ns_to_tag('Singleton')):
                # Add EntitySet to dictionary
                d_type[e_attrib.attrib['Name']] = e_attrib.attrib['Type']

            # Add type to schema dictionary
            self._graph_calls = d_type


        # Process EntityType
        for e_type in schema.iterfind(add_ns_to_tag('EntityType')):

            # Get type name
            type_name = pythonize_type(e_type.attrib['Name'])

            # Get type properties
            properties = {}
            for e_attrib in e_type.iterfind(add_ns_to_tag('Property')):
                # Add attribute to type dictionary
                properties[pythonize_attribute(e_attrib.attrib['Name'])] = pythonize_type(e_attrib.attrib['Type'])

            # Load entity navigation_properties
            navigation_properties = {}
            for e_attrib in e_type.iterfind(add_ns_to_tag('NavigationProperty')):
                # Add attribute to type dictionary
                navigation_properties[pythonize_attribute(e_attrib.attrib['Name'])] = pythonize_type(e_attrib.attrib['Type'])

            # Get entity base entity
            if 'BaseType' in e_type.attrib:
                base = pythonize_type(e_type.attrib['BaseType'])
            else:
                base = None

            # Create entity_type dictionary object
            entity_type = GraphEntityType(base_graph_type=base,
                                          properties=properties,
                                          navigation_properties=navigation_properties)

            # Add entity_type to graph_type dictionary
            self[type_name] = entity_type

        # Process ComplexType
        for e_type in schema.iterfind(add_ns_to_tag('ComplexType')):

            # Get type name
            type_name = pythonize_type(e_type.attrib['Name'])

            # Get type properties
            properties = {}
            for e_attrib in e_type.iterfind(add_ns_to_tag('Property')):
                # Add attribute to type dictionary
                properties[pythonize_attribute(e_attrib.attrib['Name'])] = pythonize_type(e_attrib.attrib['Type'])

            complex_type = GraphComplexType(properties=properties)

            # Add type to schema dictionary
            self[type_name] = complex_type

        # Process Actions
        for e_type in schema.iterfind(add_ns_to_tag('Action')):
            parameters = {}
            binding = None

            for e_attrib in e_type.iterfind(add_ns_to_tag('Parameter')):
                if e_attrib.attrib['Name'] == 'bindingParameter':
                    binding = pythonize_type(e_attrib.attrib['Type'])
                else:
                    # Add attribute type to parameters dictionary
                    parameters[pythonize_attribute(e_attrib.attrib['Name'])] = pythonize_type(e_attrib.attrib['Type'])

            if binding:
                # Load return_graph_type
                try:
                    et_return_type = next(e_type.iterfind(add_ns_to_tag('ReturnType')))
                    return_type = pythonize_type(et_return_type.attrib['Type'])
                except StopIteration:
                    return_type = None

                type_function = GraphFunction(returns=return_type,
                                              parameters=parameters)

                # Attach action to entity_type in graph_type dictionary
                self[binding].add_action(pythonize_attribute(e_type.attrib['Name']), type_function)

        # Process Functions
        for e_type in schema.iterfind(add_ns_to_tag('Function')):
            parameters = {}
            binding = None

            for e_attrib in e_type.iterfind(add_ns_to_tag('Parameter')):
                if e_attrib.attrib['Name'] == 'bindingParameter':
                    binding = pythonize_type(e_attrib.attrib['Type'])
                else:
                    # Add attribute type to parameters dictionary
                    parameters[e_attrib.attrib['Name']] = pythonize_type(e_attrib.attrib['Type'])

            if binding:
                # Load return_graph_type
                try:
                    et_return_type = next(e_type.iterfind(add_ns_to_tag('ReturnType')))
                    return_type = pythonize_type(et_return_type.attrib['Type'])
                except StopIteration:
                    return_type = None
                type_function = GraphFunction(returns=return_type,
                                              parameters=parameters)

                # Attach action to entity_type in graph_type dictionary
                self[binding].add_function(pythonize_attribute(e_type.attrib['Name']), type_function)


