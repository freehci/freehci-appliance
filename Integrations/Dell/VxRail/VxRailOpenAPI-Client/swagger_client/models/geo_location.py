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

class GeoLocation(object):
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
        'rack_name': 'str',
        'order_number': 'int'
    }

    attribute_map = {
        'rack_name': 'rack_name',
        'order_number': 'order_number'
    }

    def __init__(self, rack_name=None, order_number=None):  # noqa: E501
        """GeoLocation - a model defined in Swagger"""  # noqa: E501
        self._rack_name = None
        self._order_number = None
        self.discriminator = None
        if rack_name is not None:
            self.rack_name = rack_name
        if order_number is not None:
            self.order_number = order_number

    @property
    def rack_name(self):
        """Gets the rack_name of this GeoLocation.  # noqa: E501

        Rack name where the host is located  # noqa: E501

        :return: The rack_name of this GeoLocation.  # noqa: E501
        :rtype: str
        """
        return self._rack_name

    @rack_name.setter
    def rack_name(self, rack_name):
        """Sets the rack_name of this GeoLocation.

        Rack name where the host is located  # noqa: E501

        :param rack_name: The rack_name of this GeoLocation.  # noqa: E501
        :type: str
        """

        self._rack_name = rack_name

    @property
    def order_number(self):
        """Gets the order_number of this GeoLocation.  # noqa: E501

        Order number of the host  # noqa: E501

        :return: The order_number of this GeoLocation.  # noqa: E501
        :rtype: int
        """
        return self._order_number

    @order_number.setter
    def order_number(self, order_number):
        """Sets the order_number of this GeoLocation.

        Order number of the host  # noqa: E501

        :param order_number: The order_number of this GeoLocation.  # noqa: E501
        :type: int
        """

        self._order_number = order_number

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
        if issubclass(GeoLocation, dict):
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
        if not isinstance(other, GeoLocation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
