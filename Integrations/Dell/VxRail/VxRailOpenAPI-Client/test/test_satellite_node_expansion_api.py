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
from swagger_client.api.satellite_node_expansion_api import SatelliteNodeExpansionApi  # noqa: E501
from swagger_client.rest import ApiException


class TestSatelliteNodeExpansionApi(unittest.TestCase):
    """SatelliteNodeExpansionApi unit test stubs"""

    def setUp(self):
        self.api = SatelliteNodeExpansionApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_remove_satellite_host(self):
        """Test case for remove_satellite_host

        remove a satellite node from the host folder  # noqa: E501
        """
        pass

    def test_v1_satellite_node_expansion_cancel_post(self):
        """Test case for v1_satellite_node_expansion_cancel_post

        Cancel a failed satellite node expansion  # noqa: E501
        """
        pass

    def test_v1_satellite_node_expansion_post(self):
        """Test case for v1_satellite_node_expansion_post

        Perform a satellite node expansion  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()