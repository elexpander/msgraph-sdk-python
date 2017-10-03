"""
# Copyright (c) Microsoft Corporation.  All Rights Reserved.  Licensed under the MIT License.  See License in the project root for license information.
# 
#  This file was generated and any changes will be overwritten.
"""
from .request import GraphRequest


class GraphClient(object):
    def __init__(self, base_url, auth_provider, http_provider):
        """Initialize the :class:`GraphClient` to be
            used for all Graph API interactions

        Args:
            base_url (str): The Graph base url to use for API interactions
            auth_provider(:class:`AuthProviderBase<msgraph.auth_provider_base.AuthProviderBase>`):
                The authentication provider used by the client to auth
                with Graph services
            http_provider(:class:`HttpProviderBase<msgraph.http_provider_base.HttpProviderBase>`):
                The HTTP provider used by the client to send all 
                requests to Graph
        """
        self._base_url = base_url
        self._auth_provider = auth_provider
        self._http_provider = http_provider

    @property
    def auth_provider(self):
        """Gets and sets the client auth provider

        Returns:
            :class:`AuthProviderBase<msgraph.auth_provider_base.AuthProviderBase>`: 
            The authentication provider
        """
        return self._auth_provider

    @auth_provider.setter
    def auth_provider(self, value):
        self._auth_provider = value

    @property
    def http_provider(self):
        """Gets and sets the client HTTP provider

        Returns: 
            :class:`HttpProviderBase<msgraph.http_provider_base.HttpProviderBase>`: 
                The HTTP provider
        """
        return self._http_provider

    @http_provider.setter
    def http_provider(self, value):
        self._http_provider = value

    @property
    def base_url(self):
        """Gets and sets the base URL used by the client to make requests

        Returns:
            str: The base URL
        """
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    def request(self, resource):
        """Creates API request.
        :param resource: API resource.
        :type resource: string.
        :rtype: GraphRequest object.
        """
        if not resource.startswith(self._base_url):
            resource = self.base_url + resource
        return GraphRequest(resource, self)

    def get_page(self, api_resource, select=None, filter=None, top=None, order_by=None, count=None):
        """Returns page of objects returned by API request.
        :param api_resource: API resource.
        :type api_resource: string.
        :rtype: GraphPage object.
        """
        request = self.request(api_resource)
        request.set_query_options(select=select, filter=filter, top=top, order_by=order_by, count=count)

        return request.get()

    def get_object(self, api_resource, select=None):
        """Returns first object in page returned by API request.
        :param api_resource: API resource.
        :type api_resource: string.
        :param select: Comma separataed list of properties to get.
        :type select: string.
        :rtype: OdataObjectBase object.
        """
        request = self.request(api_resource)
        request.set_query_options(select=select)

        page = request.get()
        return next(page.objects())

    def get_value(self, api_resource):
        """Returns the value of the property requested by parameter.
        :param api_resource: API resource.
        :type api_resource: string.
        :rtype: OdataObjectBase object.
        """
        request = self.request("{}/$value".format(api_resource))
        return request.get_value()

    def create_object(self, api_resource, graph_object):
        """Sends a POST request to the specified resource with the specified body and
        returns object returned by API request.
        :param api_resource: API resource.
        :type api_resource: string.
        :param graph_object: Request body content.
        :type graph_object: OdataBaseObject or dictionary.
        :rtype: OdataObjectBase object"""
        request = self.request(api_resource)
        page = request.post(graph_object)

        return next(page.objects())

    def update_object(self, api_resource, content):
        request = self.request(api_resource)
        request.patch(content)

    def delete_object(self, api_resource):
        request = self.request(api_resource)
        request.delete()
