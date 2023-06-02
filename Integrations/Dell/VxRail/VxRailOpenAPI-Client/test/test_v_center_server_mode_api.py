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
from swagger_client.api.v_center_server_mode_api import VCenterServerModeApi  # noqa: E501
from swagger_client.rest import ApiException


class TestVCenterServerModeApi(unittest.TestCase):
    """VCenterServerModeApi unit test stubs"""

    def setUp(self):
        self.api = VCenterServerModeApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v1_vc_vc_mode_get(self):
        """Test case for v1_vc_vc_mode_get

        Get the vCenter and Platform Services Controller mode  # noqa: E501
        """
        pass

    def test_v1_vc_vc_mode_patch(self):
        """Test case for v1_vc_vc_mode_patch

        Change the vCenter and Platform Services Controller mode  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
