# -*- coding: utf-8 -*-
"""
# Copyright (c) Microsoft Corporation.  All Rights Reserved.  Licensed under the MIT License.  See License in the project root for license information.
# 
#  This file was generated and any changes will be overwritten.
"""

from __future__ import unicode_literals
from ..collection_base import CollectionPageBase
from ..model.service_plan_info import ServicePlanInfo


class ServicePlanCollection(CollectionPageBase):
    def __getitem__(self, index):
        """Get the DirectoryObject at the index specified

        Args:
            index (int): The index of the item to get from the AcceptedSendersCollectionPage

        Returns:
            :class:`DirectoryObject<msgraph.model.directory_object.DirectoryObject>`:
                The DirectoryObject at the index
        """
        return ServicePlanInfo(self._prop_list[index])
