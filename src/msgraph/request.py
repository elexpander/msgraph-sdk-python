# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .request_base import RequestBase
from collections import UserList
import json
from .model.extension import get_object_class


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

        page = GraphResponse(json.loads(self.send().content)).get_page()

        if page and page.next_page_link:
            page.set_next_page_request_client(self._client)

        return page

    def post(self, data_dict):
        """Sends POST request and gets the page content."""
        self.method = "POST"

        page = GraphResponse(json.loads(self.send(data_dict).content)).get_page()

        if page and page.next_page_link:
            page.set_next_page_request_client(self._client)

        return page


class GraphResponse(object):
    def __init__(self, data_dict):
        if isinstance(data_dict, dict):
            self._data = data_dict["value"] if "value" in data_dict else [data_dict]
            self._next_page_link = data_dict["@odata.nextLink"] if '@odata.nextLink' in data_dict else None
            self._context = data_dict["@odata.context"] if "@odata.context" in data_dict else None
        else:
            self._data = None
            self._next_page_link = None
            self._context = None

    def get_page(self):
        if self._data:
            return GraphPage(self._data, context=self._context, next_page_link=self._next_page_link)
        else:
            return None


class GraphPage(UserList):
    def __init__(self, graph_objects=[], context=None, next_page_link=None):
        super().__init__(graph_objects)
        self._context = context
        self._next_page_request = None
        self._next_page_link = next_page_link

    @property
    def context(self):
        """
        Get and set page data context for all objects on it
        :return: GraphClass
        """
        return self._context

    @context.setter
    def context(self, val):
        self._context = val

    def objects(self):
        for item in self:

            odata_type = item['@odata.type'] if '@odata.type' in item else None
            c = get_object_class(self.context, odata_type)

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

    @next_page_link.setter
    def next_page_link(self, value):
        self._next_page_link = value

    def set_next_page_request_client(self, client):
        """Initialize the next page request for the GraphPage

        Args:
            next_page_link (str): The URL for the next page request
                to be sent to
            client (:class:`GraphClient<msgraph.model.graph_client.GraphClient>`:
                The client to be used for the request
        """
        self._next_page_request = GraphRequest(self._next_page_link, client)
