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
from swagger_client.api.host_i_drac_configuration_api import HostIDRACConfigurationApi  # noqa: E501
from swagger_client.rest import ApiException


class TestHostIDRACConfigurationApi(unittest.TestCase):
    """HostIDRACConfigurationApi unit test stubs"""

    def setUp(self):
        self.api = HostIDRACConfigurationApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v1_hosts_sn_idrac_id_get(self):
        """Test case for v1_hosts_sn_idrac_id_get

        Get a list of iDRAC user slot IDs  # noqa: E501
        """
        pass

    def test_v1_hosts_sn_idrac_network_get(self):
        """Test case for v1_hosts_sn_idrac_network_get

        Get the iDRAC network settings  # noqa: E501
        """
        pass

    def test_v1_hosts_sn_idrac_network_patch(self):
        """Test case for v1_hosts_sn_idrac_network_patch

        Update the iDRAC network settings  # noqa: E501
        """
        pass

    def test_v1_hosts_sn_idrac_user_get(self):
        """Test case for v1_hosts_sn_idrac_user_get

        Get a list of iDRAC user accounts  # noqa: E501
        """
        pass

    def test_v1_hosts_sn_idrac_user_id_put(self):
        """Test case for v1_hosts_sn_idrac_user_id_put

        Update an iDRAC user account  # noqa: E501
        """
        pass

    def test_v1_hosts_sn_idrac_user_post(self):
        """Test case for v1_hosts_sn_idrac_user_post

        Create an iDRAC user account  # noqa: E501
        """
        pass

    def test_v2_hosts_sn_idrac_network_get(self):
        """Test case for v2_hosts_sn_idrac_network_get

        Get the iDRAC network settings  # noqa: E501
        """
        pass

    def test_v2_hosts_sn_idrac_network_patch(self):
        """Test case for v2_hosts_sn_idrac_network_patch

        Update the iDRAC network settings  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()