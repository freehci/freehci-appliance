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

class HostUpdateSpec(object):
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
        'geo_location': 'GeoLocation'
    }

    attribute_map = {
        'geo_location': 'geo_location'
    }

    def __init__(self, geo_location=None):  # noqa: E501
        """HostUpdateSpec - a model defined in Swagger"""  # noqa: E501
        self._geo_location = None
        self.discriminator = None
        if geo_location is not None:
            self.geo_location = geo_location

    @property
    def geo_location(self):
        """Gets the geo_location of this HostUpdateSpec.  # noqa: E501


        :return: The geo_location of this HostUpdateSpec.  # noqa: E501
        :rtype: GeoLocation
        """
        return self._geo_location

    @geo_location.setter
    def geo_location(self, geo_location):
        """Sets the geo_location of this HostUpdateSpec.


        :param geo_location: The geo_location of this HostUpdateSpec.  # noqa: E501
        :type: GeoLocation
        """

        self._geo_location = geo_location

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
        if issubclass(HostUpdateSpec, dict):
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
        if not isinstance(other, HostUpdateSpec):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
