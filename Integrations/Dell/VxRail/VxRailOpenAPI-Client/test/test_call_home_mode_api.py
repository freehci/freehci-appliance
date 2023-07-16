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
from swagger_client.api.call_home_mode_api import CallHomeModeApi  # noqa: E501
from swagger_client.rest import ApiException


class TestCallHomeModeApi(unittest.TestCase):
    """CallHomeModeApi unit test stubs"""

    def setUp(self):
        self.api = CallHomeModeApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v1_callhome_mode_get(self):
        """Test case for v1_callhome_mode_get

        Get call home mode  # noqa: E501
        """
        pass

    def test_v1_callhome_mode_put(self):
        """Test case for v1_callhome_mode_put

        Change call home mode  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()