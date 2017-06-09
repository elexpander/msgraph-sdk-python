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

    def patch(self, data_dict):
        """Sends PATCH request."""
        self.method = "PATCH"
        self.send(data_dict)

    def delete(self):
        """Sends DELETE request."""
        self.method = "DELETE"
        self.send()


class GraphResponse(object):
    def __init__(self, data_dict):
        if isinstance(data_dict, dict):
            self._data = data_dict.get("value", data_dict)
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
            return None


class GraphPage(UserList):
    def __init__(self, graph_objects=[], count=None, context=None, next_page_link=None):
        super().__init__(graph_objects)
        self._count = count
        self._context = context
        self._next_page_request = None
        self._next_page_link = next_page_link

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

    def objects(self):
        for item in self:

            odata_type = item.get('@odata.type')
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
