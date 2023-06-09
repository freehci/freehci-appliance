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
from swagger_client.api.support_logs_api import SupportLogsApi  # noqa: E501
from swagger_client.rest import ApiException


class TestSupportLogsApi(unittest.TestCase):
    """SupportLogsApi unit test stubs"""

    def setUp(self):
        self.api = SupportLogsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v1_support_logs_get(self):
        """Test case for v1_support_logs_get

        Query all of support logs  # noqa: E501
        """
        pass

    def test_v1_support_logs_id_download_get(self):
        """Test case for v1_support_logs_id_download_get

        Download the binary stream of a log  # noqa: E501
        """
        pass

    def test_v1_support_logs_id_get(self):
        """Test case for v1_support_logs_id_get

        Query the log by the log ID  # noqa: E501
        """
        pass

    def test_v1_support_logs_post(self):
        """Test case for v1_support_logs_post

        Collect the support log with the specified types of components  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
