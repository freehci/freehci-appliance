# coding: utf-8

"""
    VxRail REST API

    The VxRail REST API provides a programmatic interface for performing VxRail administrative tasks. Data is available in JSON format.  # noqa: E501

    OpenAPI spec version: 8.0.020
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class HostDiskSlotMappingsResponseVsanSlots(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'capacity': 'list[BayInfoWithDG]',
        'cache': 'list[BayInfoWithDG]'
    }

    attribute_map = {
        'capacity': 'capacity',
        'cache': 'cache'
    }

    def __init__(self, capacity=None, cache=None):  # noqa: E501
        """HostDiskSlotMappingsResponseVsanSlots - a model defined in Swagger"""  # noqa: E501
        self._capacity = None
        self._cache = None
        self.discriminator = None
        if capacity is not None:
            self.capacity = capacity
        if cache is not None:
            self.cache = cache

    @property
    def capacity(self):
        """Gets the capacity of this HostDiskSlotMappingsResponseVsanSlots.  # noqa: E501

        Contains information about slot drives claimed for capacity usage  # noqa: E501

        :return: The capacity of this HostDiskSlotMappingsResponseVsanSlots.  # noqa: E501
        :rtype: list[BayInfoWithDG]
        """
        return self._capacity

    @capacity.setter
    def capacity(self, capacity):
        """Sets the capacity of this HostDiskSlotMappingsResponseVsanSlots.

        Contains information about slot drives claimed for capacity usage  # noqa: E501

        :param capacity: The capacity of this HostDiskSlotMappingsResponseVsanSlots.  # noqa: E501
        :type: list[BayInfoWithDG]
        """

        self._capacity = capacity

    @property
    def cache(self):
        """Gets the cache of this HostDiskSlotMappingsResponseVsanSlots.  # noqa: E501

        Contains information about slot drives claimed for cache usage  # noqa: E501

        :return: The cache of this HostDiskSlotMappingsResponseVsanSlots.  # noqa: E501
        :rtype: list[BayInfoWithDG]
        """
        return self._cache

    @cache.setter
    def cache(self, cache):
        """Sets the cache of this HostDiskSlotMappingsResponseVsanSlots.

        Contains information about slot drives claimed for cache usage  # noqa: E501

        :param cache: The cache of this HostDiskSlotMappingsResponseVsanSlots.  # noqa: E501
        :type: list[BayInfoWithDG]
        """

        self._cache = cache

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(HostDiskSlotMappingsResponseVsanSlots, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, HostDiskSlotMappingsResponseVsanSlots):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
