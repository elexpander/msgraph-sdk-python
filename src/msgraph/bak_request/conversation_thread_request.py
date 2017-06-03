# -*- coding: utf-8 -*- 
"""
# Copyright (c) Microsoft Corporation.  All Rights Reserved.  Licensed under the MIT License.  See License in the project root for license information.
# 
#  This file was generated and any changes will be overwritten.
"""

from ..request_base import RequestBase
from ..model.conversation_thread import ConversationThread
import json
import asyncio

class ConversationThreadRequest(RequestBase):
    """The type ConversationThreadRequest."""
    
    def __init__(self, request_url, client, options):
        """Constructs a new ConversationThreadRequest.

        Args:
            request_url (str): The url to perform the ConversationThreadRequest
                on
            client (:class:`GraphClient<msgraph.request.graph_client.GraphClient>`):
                The client which will be used for the request
            options (list of :class:`Option<msgraph.options.Option>`):
                A list of options to pass into the request
        """
        super(ConversationThreadRequest, self).__init__(request_url, client, options)

    def delete(self):
        """Deletes the specified ConversationThread."""
        self.method = "DELETE"
        self.send()

    @asyncio.coroutine
    def delete_async(self):
        """Deletes the specified ConversationThread."""
        future = self._client._loop.run_in_executor(None,
                                                    self.delete)
        yield from future

    def get(self):
        """Gets the specified ConversationThread.
        
        Returns:
            :class:`ConversationThread<msgraph.model.conversation_thread.ConversationThread>`:
                The ConversationThread.
        """
        self.method = "GET"
        entity = ConversationThread(json.loads(self.send().content))
        self._initialize_collection_properties(entity)
        return entity

    @asyncio.coroutine
    def get_async(self):
        """Gets the specified ConversationThread in async.

        Yields:
            :class:`ConversationThread<msgraph.model.conversation_thread.ConversationThread>`:
                The ConversationThread.
        """
        future = self._client._loop.run_in_executor(None,
                                                    self.get)
        entity = yield from future
        return entity

    def update(self, conversation_thread):
        """Updates the specified ConversationThread.
        
        Args:
            conversation_thread (:class:`ConversationThread<msgraph.model.conversation_thread.ConversationThread>`):
                The ConversationThread to update.

        Returns:
            :class:`ConversationThread<msgraph.model.conversation_thread.ConversationThread>`:
                The updated ConversationThread.
        """
        self.content_type = "application/json"
        self.method = "PATCH"
        entity = ConversationThread(json.loads(self.send(conversation_thread).content))
        self._initialize_collection_properties(entity)
        return entity

    @asyncio.coroutine
    def update_async(self, conversation_thread):
        """Updates the specified ConversationThread in async
        
        Args:
            conversation_thread (:class:`ConversationThread<msgraph.model.conversation_thread.ConversationThread>`):
                The ConversationThread to update.

        Yields:
            :class:`ConversationThread<msgraph.model.conversation_thread.ConversationThread>`:
                The updated ConversationThread.
        """
        future = self._client._loop.run_in_executor(None,
                                                    self.update,
                                                    conversation_thread)
        entity = yield from future
        return entity

    def _initialize_collection_properties(self, value):
        if value and value._prop_dict:
            if value.to_recipients and value.to_recipients._prop_dict:
                if "to_recipients@odata.nextLink" in value._prop_dict:
                    next_page_link = value._prop_dict["to_recipients@odata.nextLink"]
                    value.to_recipients._init_next_page_request(next_page_link, self._client, None)
            if value.cc_recipients and value.cc_recipients._prop_dict:
                if "cc_recipients@odata.nextLink" in value._prop_dict:
                    next_page_link = value._prop_dict["cc_recipients@odata.nextLink"]
                    value.cc_recipients._init_next_page_request(next_page_link, self._client, None)
            if value.posts and value.posts._prop_dict:
                if "posts@odata.nextLink" in value._prop_dict:
                    next_page_link = value._prop_dict["posts@odata.nextLink"]
                    value.posts._init_next_page_request(next_page_link, self._client, None)
