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

    def append_to_request_url(self, url_segment):
        """Appends a URL portion to the current request URL

        Args:
            url_segment (str): The segment you would like to append
                to the existing request URL.
        """
        return self._request_url + "/" + url_segment

    def get_value(self):
        """Gets single just the value from a property. No JSON data is returned.
        :returns: value
        """
        self.method = "GET"
        return self.send().content

    def get(self):
        """Sends GET request and returns data.
        :returns GraphPage with data returned by request.
        """
        self.method = "GET"
        return GraphResponse(json.loads(self.send().content)).get_page()

    def post(self, data_dict):
        """Sends POST request and gets the page content.
        :param data_dict: dictionary with request data.
        :returns GraphPage with data returned by request.
        """
        self.method = "POST"
        return GraphResponse(json.loads(self.send(data_dict).content)).get_page()

    def patch(self, data_dict):
        """Sends PATCH request.
        :param data_dict: dictionary with request data.
        """
        self.method = "PATCH"
        self.send(data_dict)

    def delete(self):
        """Sends DELETE request."""
        self.method = "DELETE"
        self.send()


class GraphResponse(object):
    def __init__(self, data_dict):
        if isinstance(data_dict, dict):
            # Data is a collection in value or it's a single item which we convert to list of single item
            self._data = data_dict.get("value", [data_dict])
            self._count = data_dict.get("@odata.count")
            self._next_page_link = data_dict.get("@odata.nextLink")
            self._context = data_dict.get("@odata.context")
        else:
            self._data = None
            self._count = None
            self._next_page_link = None
            self._context = None

    def get_page(self):
        if self._data:
            return GraphPage(self._data, count=self._count, context=self._context, next_page_link=self._next_page_link)
        else:
            return GraphPage(None)


class GraphPage(UserList):
    def __init__(self, graph_objects=[], count=None, context=None, next_page_link=None):
        super().__init__(graph_objects)
        self._count = count
        self._context = context
        self._next_page_request = None
        self._next_page_link = next_page_link

    def __getitem__(self, item):
        object_dict = super().__getitem__(item)
        c = get_object_class(self.context, object_dict.get('@odata.type'))
        return c(object_dict)

    @property
    def api_count(self):
        """Count returned by API when it's requested."""
        return self._count

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
