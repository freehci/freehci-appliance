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
from swagger_client.api.system_pre_check_api import SystemPreCheckApi  # noqa: E501
from swagger_client.rest import ApiException


class TestSystemPreCheckApi(unittest.TestCase):
    """SystemPreCheckApi unit test stubs"""

    def setUp(self):
        self.api = SystemPreCheckApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v1_system_precheck_post(self):
        """Test case for v1_system_precheck_post

        Perform a pre-check  # noqa: E501
        """
        pass

    def test_v1_system_precheck_results_get(self):
        """Test case for v1_system_precheck_results_get

        Get all pre-check reports  # noqa: E501
        """
        pass

    def test_v1_system_precheck_results_id_get(self):
        """Test case for v1_system_precheck_results_id_get

        Get a pre-check result  # noqa: E501
        """
        pass

    def test_v1_system_prechecks_profiles_get(self):
        """Test case for v1_system_prechecks_profiles_get

        List pre-check profiles  # noqa: E501
        """
        pass

    def test_v1_system_prechecks_version_get(self):
        """Test case for v1_system_prechecks_version_get

        Get the pre-check version  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
