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
from swagger_client.api.system_proxy_settings_api import SystemProxySettingsApi  # noqa: E501
from swagger_client.rest import ApiException


class TestSystemProxySettingsApi(unittest.TestCase):
    """SystemProxySettingsApi unit test stubs"""

    def setUp(self):
        self.api = SystemProxySettingsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v1_system_proxy_delete(self):
        """Test case for v1_system_proxy_delete

        Disable VxRail Manager system proxy settings  # noqa: E501
        """
        pass

    def test_v1_system_proxy_get(self):
        """Test case for v1_system_proxy_get

        Get the VxRail Manager system proxy settings  # noqa: E501
        """
        pass

    def test_v1_system_proxy_patch(self):
        """Test case for v1_system_proxy_patch

        Update VxRail Manager system proxy settings  # noqa: E501
        """
        pass

    def test_v1_system_proxy_post(self):
        """Test case for v1_system_proxy_post

        Enable VxRail Manager system proxy settings  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
