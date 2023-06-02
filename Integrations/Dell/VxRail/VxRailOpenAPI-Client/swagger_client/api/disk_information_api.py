# coding: utf-8

"""
    VxRail REST API

    The VxRail REST API provides a programmatic interface for performing VxRail administrative tasks. Data is available in JSON format.  # noqa: E501

    OpenAPI spec version: 8.0.020
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from swagger_client.api_client import ApiClient


class DiskInformationApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def v1_disks_get(self, **kwargs):  # noqa: E501
        """Get a list of disks  # noqa: E501

        Retrieve a list of disk drives and their associated information.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.v1_disks_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: list[DiskInfo]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.v1_disks_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.v1_disks_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def v1_disks_get_with_http_info(self, **kwargs):  # noqa: E501
        """Get a list of disks  # noqa: E501

        Retrieve a list of disk drives and their associated information.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.v1_disks_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: list[DiskInfo]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method v1_disks_get" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['basicAuth']  # noqa: E501

        return self.api_client.call_api(
            '/v1/disks', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[DiskInfo]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def v1_disks_sn_get(self, disk_sn, **kwargs):  # noqa: E501
        """Get information about a disk  # noqa: E501

        Retrieve information about a specific disk drive.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.v1_disks_sn_get(disk_sn, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str disk_sn: The serial number of disk that you want to query. (required)
        :return: DiskInfo
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.v1_disks_sn_get_with_http_info(disk_sn, **kwargs)  # noqa: E501
        else:
            (data) = self.v1_disks_sn_get_with_http_info(disk_sn, **kwargs)  # noqa: E501
            return data

    def v1_disks_sn_get_with_http_info(self, disk_sn, **kwargs):  # noqa: E501
        """Get information about a disk  # noqa: E501

        Retrieve information about a specific disk drive.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.v1_disks_sn_get_with_http_info(disk_sn, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str disk_sn: The serial number of disk that you want to query. (required)
        :return: DiskInfo
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['disk_sn']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method v1_disks_sn_get" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'disk_sn' is set
        if ('disk_sn' not in params or
                params['disk_sn'] is None):
            raise ValueError("Missing the required parameter `disk_sn` when calling `v1_disks_sn_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'disk_sn' in params:
            path_params['disk_sn'] = params['disk_sn']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['basicAuth']  # noqa: E501

        return self.api_client.call_api(
            '/v1/disks/{disk_sn}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='DiskInfo',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
