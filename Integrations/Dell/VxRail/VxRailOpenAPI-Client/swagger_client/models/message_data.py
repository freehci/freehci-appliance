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

class MessageData(object):
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
        'id': 'str',
        'kb': 'str',
        'action': 'str',
        'alphaid': 'str',
        'symptom': 'str',
        'severity': 'str'
    }

    attribute_map = {
        'id': 'id',
        'kb': 'kb',
        'action': 'action',
        'alphaid': 'alphaid',
        'symptom': 'symptom',
        'severity': 'severity'
    }

    def __init__(self, id=None, kb=None, action=None, alphaid=None, symptom=None, severity=None):  # noqa: E501
        """MessageData - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._kb = None
        self._action = None
        self._alphaid = None
        self._symptom = None
        self._severity = None
        self.discriminator = None
        if id is not None:
            self.id = id
        if kb is not None:
            self.kb = kb
        if action is not None:
            self.action = action
        if alphaid is not None:
            self.alphaid = alphaid
        if symptom is not None:
            self.symptom = symptom
        if severity is not None:
            self.severity = severity

    @property
    def id(self):
        """Gets the id of this MessageData.  # noqa: E501


        :return: The id of this MessageData.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this MessageData.


        :param id: The id of this MessageData.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def kb(self):
        """Gets the kb of this MessageData.  # noqa: E501

        kb number  # noqa: E501

        :return: The kb of this MessageData.  # noqa: E501
        :rtype: str
        """
        return self._kb

    @kb.setter
    def kb(self, kb):
        """Sets the kb of this MessageData.

        kb number  # noqa: E501

        :param kb: The kb of this MessageData.  # noqa: E501
        :type: str
        """

        self._kb = kb

    @property
    def action(self):
        """Gets the action of this MessageData.  # noqa: E501


        :return: The action of this MessageData.  # noqa: E501
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this MessageData.


        :param action: The action of this MessageData.  # noqa: E501
        :type: str
        """

        self._action = action

    @property
    def alphaid(self):
        """Gets the alphaid of this MessageData.  # noqa: E501


        :return: The alphaid of this MessageData.  # noqa: E501
        :rtype: str
        """
        return self._alphaid

    @alphaid.setter
    def alphaid(self, alphaid):
        """Sets the alphaid of this MessageData.


        :param alphaid: The alphaid of this MessageData.  # noqa: E501
        :type: str
        """

        self._alphaid = alphaid

    @property
    def symptom(self):
        """Gets the symptom of this MessageData.  # noqa: E501


        :return: The symptom of this MessageData.  # noqa: E501
        :rtype: str
        """
        return self._symptom

    @symptom.setter
    def symptom(self, symptom):
        """Sets the symptom of this MessageData.


        :param symptom: The symptom of this MessageData.  # noqa: E501
        :type: str
        """

        self._symptom = symptom

    @property
    def severity(self):
        """Gets the severity of this MessageData.  # noqa: E501


        :return: The severity of this MessageData.  # noqa: E501
        :rtype: str
        """
        return self._severity

    @severity.setter
    def severity(self, severity):
        """Sets the severity of this MessageData.


        :param severity: The severity of this MessageData.  # noqa: E501
        :type: str
        """

        self._severity = severity

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
        if issubclass(MessageData, dict):
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
        if not isinstance(other, MessageData):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
