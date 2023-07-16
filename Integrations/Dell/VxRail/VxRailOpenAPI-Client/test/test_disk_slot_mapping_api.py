# coding: utf-8

"""
    VxRail REST API

    The VxRail REST API provides a programmatic interface for performing VxRail administrative tasks. Data is available in JSON format.  # noqa: E501

    OpenAPI spec version: 8.0.020
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import unittest

import swagger_client
from swagger_client.api.disk_slot_mapping_api import DiskSlotMappingApi  # noqa: E501
from swagger_client.rest import ApiException


class TestDiskSlotMappingApi(unittest.TestCase):
    """DiskSlotMappingApi unit test stubs"""

    def setUp(self):
        self.api = DiskSlotMappingApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v1_hosts_disk_slot_mappings_get(self):
        """Test case for v1_hosts_disk_slot_mappings_get

        Get disk slot mappings for hosts  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()