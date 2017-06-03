"""
Copyright (c) Microsoft Corporation.  All Rights Reserved.  Licensed under the MIT License.  See License in the project root for license information.
"""

from __future__ import unicode_literals


class GraphError(Exception):

    def __init__(self, prop_dict, status_code):
        """Initialize a GraphError given the JSON
        error response dictionary, and the HTTP status code

        Args:
            prop_dict (dict): A dictionary containing the response from Graph
            status_code (int): The HTTP status code (ex. 200, 201, etc.)
        """
        error_code = prop_dict["code"] if "code" in prop_dict else ErrorCode.Malformed
        message = prop_dict["message"] if "message" in prop_dict else "The received response was malformed."

        super().__init__(str(error_code) + " - " + message)
        self._status_code = status_code
        self._error_code = error_code
        self._message = message

    @property
    def status_code(self):
        """The HTTP status code."""
        return self._status_code

    @property
    def code(self):
        """The Graph error code sent back in the response. Possible codes can be found in the :class:`ErrorCode` enum.
        :return str: The error code
        """
        return self._error_code

    @property
    def message(self):
        """The Graph error message sent back in the response."""
        return self._message

    @property
    def inner_error(self):
        """Creates a GraphError object from the specified inner
        error within the response.

        Returns:
            :class:`GraphError`: Error from within the inner
                response
        """
        return Exception(self.message, self.status_code) if self.message else None

    def matches(self, code):
        """Recursively searches the :class:`GraphError` to find
        if the specified code was found

        Args:
            code (str): The error code to search for

        Returns:
            bool: True if the error code was found, false otherwise
        """
        if self.code == code:
            return True

        return False if self.inner_error is None else self.inner_error.matches(code)


class ErrorCode(object):
    #: Access was denied to the resource
    AccessDenied = "accessDenied"
    #: The activity limit has been reached
    ActivityLimitReached = "activityLimitReached"
    #: A general exception occured
    GeneralException = "generalException"
    #: An invalid range was provided
    InvalidRange = "invalidRange"
    #: An invalid request was provided
    InvalidRequest = "invalidRequest"
    #: The requested resource was not found
    ItemNotFound = "itemNotFound"
    #: Malware was detected in the resource
    MalwareDetected = "malwareDetected"
    #: The name already exists
    NameAlreadyExists = "nameAlreadyExists"
    #: The action was not allowed
    NotAllowed = "notAllowed"
    #: The action was not supported
    NotSupported = "notSupported"
    #: The resource was modified
    ResourceModified = "resourceModified"
    #: A resync is required
    ResyncRequired = "resyncRequired"
    #: The Graph service is not available
    ServiceNotAvailable = "serviceNotAvailable"
    #: The quota for this OneDrive has been reached
    QuotaLimitReached = "quotaLimitReached"
    #: The user is unauthenticated
    Unauthenticated = "unauthenticated"

    #: The response was malformed
    Malformed = "malformed"
