# -*- coding: utf-8 -*-
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

    def request(self, api_call):
        return GraphRequest(self.base_url + api_call, self)

    def get_page(self, api_call):
        return GraphRequest(self.base_url + api_call, self).get()

    def get_object(self, api_call):
        page = GraphRequest(self.base_url + api_call, self).get()
        return next(page.objects())
