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

class StorageInfoSlotClaims(object):
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
        'usage': 'str',
        'values': 'list[StorageInfoValues]'
    }

    attribute_map = {
        'usage': 'usage',
        'values': 'values'
    }

    def __init__(self, usage=None, values=None):  # noqa: E501
        """StorageInfoSlotClaims - a model defined in Swagger"""  # noqa: E501
        self._usage = None
        self._values = None
        self.discriminator = None
        if usage is not None:
            self.usage = usage
        if values is not None:
            self.values = values

    @property
    def usage(self):
        """Gets the usage of this StorageInfoSlotClaims.  # noqa: E501

        The type of usage the slot values are claimed as  # noqa: E501

        :return: The usage of this StorageInfoSlotClaims.  # noqa: E501
        :rtype: str
        """
        return self._usage

    @usage.setter
    def usage(self, usage):
        """Sets the usage of this StorageInfoSlotClaims.

        The type of usage the slot values are claimed as  # noqa: E501

        :param usage: The usage of this StorageInfoSlotClaims.  # noqa: E501
        :type: str
        """
        allowed_values = ["non-vSAN"]  # noqa: E501
        if usage not in allowed_values:
            raise ValueError(
                "Invalid value for `usage` ({0}), must be one of {1}"  # noqa: E501
                .format(usage, allowed_values)
            )

        self._usage = usage

    @property
    def values(self):
        """Gets the values of this StorageInfoSlotClaims.  # noqa: E501


        :return: The values of this StorageInfoSlotClaims.  # noqa: E501
        :rtype: list[StorageInfoValues]
        """
        return self._values

    @values.setter
    def values(self, values):
        """Sets the values of this StorageInfoSlotClaims.


        :param values: The values of this StorageInfoSlotClaims.  # noqa: E501
        :type: list[StorageInfoValues]
        """

        self._values = values

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
        if issubclass(StorageInfoSlotClaims, dict):
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
        if not isinstance(other, StorageInfoSlotClaims):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
