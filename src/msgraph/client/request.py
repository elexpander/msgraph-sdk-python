# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .request_base import RequestBase
from collections import UserList
import json
from ..model2.auxiliary import get_object_class


class GraphRequest(RequestBase):
    def __init__(self, request_url, client):
        """Initialize the UsersCollectionRequest

        Args:
            request_url (str): The url to perform the UsersCollectionRequest
                on
            client (:class:`GraphClient<msgraph.request.graph_client.GraphClient>`):
                The client which will be used for the request
        """
        super().__init__(request_url, client, None)

    def get(self):
        """Gets the GraphPage

        Returns: 
            :class:`GraphPage<msgraph.request.users_collection.GraphPage>`:
                The GraphPage
        """
        self.method = "GET"

        response_dict = json.loads(self.send().content)
        if response_dict:

            if "value" in response_dict:
                page = GraphPage(response_dict["value"])
            else:
                page = GraphPage([response_dict])

            if '@odata.nextLink' in response_dict:
                page.set_next_page_request(response_dict["@odata.nextLink"], self._client)

            if "@odata.context" in response_dict:
                page.data_context = response_dict["@odata.context"]
            return page

        return None


class GraphPage(UserList):
    def __init__(self, graph_objects=[]):
        super().__init__(graph_objects)
        self._data_context = ''
        self._next_page_request = None
        self._next_page_link = None

    @property
    def data_context(self):
        """
        Get and set page data context for all objects on it
        :return: GraphClass
        """
        return self._data_context

    @data_context.setter
    def data_context(self, val):
        self._data_context = val

    def objects(self):
        for item in self:

            odata_type = item['@odata.type'] if '@odata.type' in item else None
            c =get_object_class(self.data_context, odata_type)

            yield c(item)

    @property
    def next_page_request(self):
        """Gets a request for the next page of a collection, if one exists

        Returns:
            The request object to send
        """
        return self._next_page_request

    @property
    def next_page_link(self):
        return self._next_page_link

    def set_next_page_request(self, next_page_link, client):
        """Initialize the next page request for the GraphPage

        Args:
            next_page_link (str): The URL for the next page request
                to be sent to
            client (:class:`GraphClient<msgraph.model.graph_client.GraphClient>`:
                The client to be used for the request
        """
        self._next_page_link = next_page_link
        self._next_page_request = GraphRequest(next_page_link, client)
