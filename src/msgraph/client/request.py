# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .request_base import RequestBase
from .model import GraphSchema
from collections import UserList
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
                # It's a collection of entities
                # "@odata.context"
                page = GraphPage(response_dict["value"])
                page.data_context = response_dict["@odata.context"]

                if '@odata.nextLink' in response_dict:
                    page.set_next_page_request(response_dict["@odata.nextLink"], self._client)
            else:
                # It's an entity
                page = GraphPage([response_dict])
                page.data_context = response_dict["@odata.context"]
            return page

        return None


class GraphPage(UserList):
    def __init__(self, graph_objects=[]):
        super().__init__(graph_objects)
        self._data_context = ''
        self._next_page_request = None

    @property
    def data_context(self):
        """
        Get and set page data context for all objects on it
        :return: GraphClass
        """
        return self._data_context

    @data_context.setter
    def data_context(self, val):
        pos = val.find('#')
        self._data_context = val[pos+1:]

    def objects(self):
        for item in self:
            if '@odata.type' in item:
                class_name = GraphSchema.get_python_tag(item['@odata.type'])
            else:
                class_name = GraphSchema.get_python_tag(tag=None, context=self.data_context)
            yield GraphSchema.get_class(class_name)(item)

    @property
    def next_page_request(self):
        """Gets a request for the next page of a collection, if one exists

        Returns:
            The request object to send
        """
        return self._next_page_request

    def set_next_page_request(self, next_page_link, client):
        """Initialize the next page request for the GraphPage

        Args:
            next_page_link (str): The URL for the next page request
                to be sent to
            client (:class:`GraphClient<msgraph.model.graph_client.GraphClient>`:
                The client to be used for the request
        """
        self._next_page_request = GraphRequest(next_page_link, client)
