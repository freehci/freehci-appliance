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

class VlcmImageDepotInfo(object):
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
        'base_image': 'VlcmImageDepotInfoBaseImage',
        'components': 'dict(str, str)',
        'hardware_support': 'dict(str, VlcmImageDepotInfoHardwareSupport)'
    }

    attribute_map = {
        'base_image': 'base_image',
        'components': 'components',
        'hardware_support': 'hardware_support'
    }

    def __init__(self, base_image=None, components=None, hardware_support=None):  # noqa: E501
        """VlcmImageDepotInfo - a model defined in Swagger"""  # noqa: E501
        self._base_image = None
        self._components = None
        self._hardware_support = None
        self.discriminator = None
        if base_image is not None:
            self.base_image = base_image
        if components is not None:
            self.components = components
        if hardware_support is not None:
            self.hardware_support = hardware_support

    @property
    def base_image(self):
        """Gets the base_image of this VlcmImageDepotInfo.  # noqa: E501


        :return: The base_image of this VlcmImageDepotInfo.  # noqa: E501
        :rtype: VlcmImageDepotInfoBaseImage
        """
        return self._base_image

    @base_image.setter
    def base_image(self, base_image):
        """Sets the base_image of this VlcmImageDepotInfo.


        :param base_image: The base_image of this VlcmImageDepotInfo.  # noqa: E501
        :type: VlcmImageDepotInfoBaseImage
        """

        self._base_image = base_image

    @property
    def components(self):
        """Gets the components of this VlcmImageDepotInfo.  # noqa: E501


        :return: The components of this VlcmImageDepotInfo.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._components

    @components.setter
    def components(self, components):
        """Sets the components of this VlcmImageDepotInfo.


        :param components: The components of this VlcmImageDepotInfo.  # noqa: E501
        :type: dict(str, str)
        """

        self._components = components

    @property
    def hardware_support(self):
        """Gets the hardware_support of this VlcmImageDepotInfo.  # noqa: E501


        :return: The hardware_support of this VlcmImageDepotInfo.  # noqa: E501
        :rtype: dict(str, VlcmImageDepotInfoHardwareSupport)
        """
        return self._hardware_support

    @hardware_support.setter
    def hardware_support(self, hardware_support):
        """Sets the hardware_support of this VlcmImageDepotInfo.


        :param hardware_support: The hardware_support of this VlcmImageDepotInfo.  # noqa: E501
        :type: dict(str, VlcmImageDepotInfoHardwareSupport)
        """

        self._hardware_support = hardware_support

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
        if issubclass(VlcmImageDepotInfo, dict):
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
        if not isinstance(other, VlcmImageDepotInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other