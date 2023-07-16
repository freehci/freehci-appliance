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

class Day1RequestValidationInfoCursoryErrors(object):
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
        'fields': 'list[Day1RequestValidationFieldInfo]',
        'generals': 'list[Day1RequestValidationGeneralInfo]'
    }

    attribute_map = {
        'fields': 'fields',
        'generals': 'generals'
    }

    def __init__(self, fields=None, generals=None):  # noqa: E501
        """Day1RequestValidationInfoCursoryErrors - a model defined in Swagger"""  # noqa: E501
        self._fields = None
        self._generals = None
        self.discriminator = None
        if fields is not None:
            self.fields = fields
        if generals is not None:
            self.generals = generals

    @property
    def fields(self):
        """Gets the fields of this Day1RequestValidationInfoCursoryErrors.  # noqa: E501


        :return: The fields of this Day1RequestValidationInfoCursoryErrors.  # noqa: E501
        :rtype: list[Day1RequestValidationFieldInfo]
        """
        return self._fields

    @fields.setter
    def fields(self, fields):
        """Sets the fields of this Day1RequestValidationInfoCursoryErrors.


        :param fields: The fields of this Day1RequestValidationInfoCursoryErrors.  # noqa: E501
        :type: list[Day1RequestValidationFieldInfo]
        """

        self._fields = fields

    @property
    def generals(self):
        """Gets the generals of this Day1RequestValidationInfoCursoryErrors.  # noqa: E501


        :return: The generals of this Day1RequestValidationInfoCursoryErrors.  # noqa: E501
        :rtype: list[Day1RequestValidationGeneralInfo]
        """
        return self._generals

    @generals.setter
    def generals(self, generals):
        """Sets the generals of this Day1RequestValidationInfoCursoryErrors.


        :param generals: The generals of this Day1RequestValidationInfoCursoryErrors.  # noqa: E501
        :type: list[Day1RequestValidationGeneralInfo]
        """

        self._generals = generals

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
        if issubclass(Day1RequestValidationInfoCursoryErrors, dict):
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
        if not isinstance(other, Day1RequestValidationInfoCursoryErrors):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other