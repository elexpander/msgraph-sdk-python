# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .request_base import RequestBase
import json


class GraphRequest(RequestBase):
    def __init__(self, request_url, client):
        """Initialize the UsersCollectionRequest

        Args:
            request_url (str): The url to perform the UsersCollectionRequest
                on
            client (:class:`GraphClient<msgraph.request.graph_client.GraphClient>`):
                The client which will be used for the request
        """
        super(GraphRequest, self).__init__(request_url, client, None)

    def get(self):
        """Gets the GraphPage

        Returns: 
            :class:`GraphPage<msgraph.request.users_collection.GraphPage>`:
                The GraphPage
        """
        self.method = "GET"

        response_dict = json.loads(self.send().content)
        if response_dict:

            if 'value' in response_dict:
                # It's a collection
                page = GraphPage(response_dict["value"])
                if '@odata.nextLink' in response_dict:
                    page.set_next_page_request(response_dict["@odata.nextLink"], self._client)
            else:
                # It's a unique object
                page = GraphPage(response_dict)
            return page

        return None


class GraphPage(object):
    def __init__(self, graph_objects=[]):
        self._graph_objects = graph_objects
        self._next_page_request = None

    def __len__(self):
        return len(self._graph_objects)

    def __str__(self):
        """Returns a string representation of the object
        including object type and all properties

        Returns:
            string
        """
        output = '<MSGRAPH ' + type(self).__name__ + ': {\n'
        for obj in self._graph_objects:
            output = output + str(obj) + ",\n"
        output = output + '}>'
        return output

    def __getitem__(self, index):
        """Get the User at the index specified

        Args:
            index (int): The index of the item to get from the GraphPage

        Returns:
            :class:`User<msgraph.model.user.User>`:
                The User at the index
        """
        obj = self._graph_objects[index]
        return obj

    def users(self):
        """Get a generator of User within the GraphPage

        Yields:
            :class:`User<msgraph.model.user.User>`:
                The next User in the collection
        """
        for item in self._prop_list:
            yield User(item)

    @property
    def next_page_request(self):
        """Gets a request for the next page of a collection, if one exists

        Returns:
            The request object to send
        """
        try:
            return self._next_page_request
        except:
            return None

    def set_next_page_request(self, next_page_link, client):
        """Initialize the next page request for the GraphPage

        Args:
            next_page_link (str): The URL for the next page request
                to be sent to
            client (:class:`GraphClient<msgraph.model.graph_client.GraphClient>`:
                The client to be used for the request
        """
        self._next_page_request = GraphRequest(next_page_link, client)
