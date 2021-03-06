"""
Copyright (c) Microsoft Corporation.  All Rights Reserved.  Licensed under the MIT License.  See License in the project root for license information.
"""
from __future__ import generators
from __future__ import unicode_literals
from .version import __version__
from .options import *
from .model.odata_object_base import OdataObjectBase
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


class RequestBase(object):

    def __init__(self, request_url, client, options):
        """Initialize a request to be sent

        Args:
            request_url (str): The URL to send the request to
            client (:class:`GraphClient<microsoft.requests.one_drive_client.GraphClient>`):
                The client used to make the requests
            options (list of :class:`Option<microsoft.options.Option>`):
                A list of options to add to the request
        """
        self._client = client
        self._request_url = request_url
        self._response = None
        self._headers = {}
        self._query_options = {}
        self._content_type = None
        self._method = None

        if options:
            header_list = [
                pair for pair in options if isinstance(pair, HeaderOption)]
            self._headers = {pair.key: pair.value for pair in header_list}

            query_list = [
                pair for pair in options if isinstance(pair, QueryOption)]
            self._query_options = {pair.key: pair.value for pair in query_list}

    @property
    def request_url(self):
        """Gets the request URL with query string appended

        Returns:
            str: The request URL
        """
        url_parts = list(urlparse(self._request_url))
        query_dict = dict(parse_qsl(url_parts[4]))
        self._query_options.update(query_dict)
        url_parts[4] = urlencode(self._query_options)
        return urlunparse(url_parts)

    @property
    def response(self):
        return self._response

    @property
    def content_type(self):
        """Gets and sets the content-type header of the request
        (ex. application/x-www-form-urlencoded)

        Returns:
            str: The request content-type
        """
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = value

    @property
    def method(self):
        """Gets and sets the HTTP method by which to send the
        request (ex. PUT, GET)

        Returns:
            str: The HTTP method
        """
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

    def append_option(self, option):
        """Appends an option to the request

        Args:
            option (:class:`Option<microsoft.options.Option>`):
                The option to append to the request
        """
        if isinstance(option, HeaderOption):
            self._headers[option.key] = option.value
        elif isinstance(option, QueryOption):
            self._query_options[option.key] = option.value

    def send(self, content=None, path=None):
        """Send the request using the client specified at request initialization.
        :param content:str: Defaults to None, the body of the request that will be sent
        :param path:str: Defaults to None, the local path of the file which will be sent
        :return HttpResponse: The response to the request
        """
        self._client.auth_provider.authenticate_request(self)

        self.append_option(HeaderOption("Content-Type", "application/json"))
        self.append_option(HeaderOption("X-RequestStats", "SDK-Version=python-v"+__version__))

        if self._content_type:
            self.append_option(HeaderOption("Content-Type", self._content_type))

        if path:
            self._response = self._client.http_provider.send(self._method,
                                                             self._headers,
                                                             self._request_url,
                                                             path=path)
        else:
            content_dict = None

            if content:
                if isinstance(content, OdataObjectBase):
                    content_dict = content.serialized()
                elif isinstance(content, dict):
                    content_dict = content
                else:
                    raise ValueError("Request body must be JSON serializable.")

            self._response = self._client.http_provider.send(self._method,
                                                             self._headers,
                                                             self.request_url,
                                                             content=content_dict)
        return self._response

    def download_item(self, path):
        """Download a file to a local path

        Args:
            path (str): The local path to download the file

        Returns:
            :class:`HttpResponse<microsoft.http_response.HttpResponse>`:
                The response to the request 
        """
        self._client.auth_provider.authenticate_request(self)

        self.append_option(HeaderOption("X-RequestStats",
                                        "SDK-Version=python-v"+__version__))

        if self._content_type:
            self.append_option(HeaderOption("Content-Type", self._content_type))

        response = self._client.http_provider.download(
            self._headers,
            self.request_url,
            path)

        return response

    def set_query_options(self, expand=None, select=None, filter=None, top=None, order_by=None, count=False):
        """Adds query options from a set of known parameters

        Args:
            expand (str): Default None, comma-seperated list of relationships
                to expand in the response.
            select (str): Default None, comma-seperated list of properties to
                include in the response.
            filter (str): Default None, an odata compliant filter
            top (int): Default None, the number of items to return in a result.
            order_by (str): Default None, comma-seperated list of properties
                that are used to sort the order of items in the response.
            count (bool): Default to False, set to True to get count of objects in result.
        """
        if expand:
            self.append_option(QueryOption("$expand", expand))

        if select:
            self.append_option(QueryOption("$select", select))

        if filter:
            self.append_option(QueryOption("$filter", filter))

        if top:
            self.append_option(QueryOption("$top", str(top)))

        if order_by:
            self.append_option(QueryOption("$orderby", order_by))

        if count:
            self.append_option(QueryOption("$count", "true"))