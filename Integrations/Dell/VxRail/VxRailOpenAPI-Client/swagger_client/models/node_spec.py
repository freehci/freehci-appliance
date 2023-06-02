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

class NodeSpec(object):
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
        'sn': 'str',
        'version': 'str',
        'ip': 'str',
        'root_user': 'str',
        'root_password': 'str'
    }

    attribute_map = {
        'sn': 'sn',
        'version': 'version',
        'ip': 'ip',
        'root_user': 'root_user',
        'root_password': 'root_password'
    }

    def __init__(self, sn=None, version=None, ip=None, root_user=None, root_password=None):  # noqa: E501
        """NodeSpec - a model defined in Swagger"""  # noqa: E501
        self._sn = None
        self._version = None
        self._ip = None
        self._root_user = None
        self._root_password = None
        self.discriminator = None
        if sn is not None:
            self.sn = sn
        if version is not None:
            self.version = version
        if ip is not None:
            self.ip = ip
        if root_user is not None:
            self.root_user = root_user
        if root_password is not None:
            self.root_password = root_password

    @property
    def sn(self):
        """Gets the sn of this NodeSpec.  # noqa: E501

        serial number of node  # noqa: E501

        :return: The sn of this NodeSpec.  # noqa: E501
        :rtype: str
        """
        return self._sn

    @sn.setter
    def sn(self, sn):
        """Sets the sn of this NodeSpec.

        serial number of node  # noqa: E501

        :param sn: The sn of this NodeSpec.  # noqa: E501
        :type: str
        """

        self._sn = sn

    @property
    def version(self):
        """Gets the version of this NodeSpec.  # noqa: E501

        install version of node  # noqa: E501

        :return: The version of this NodeSpec.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this NodeSpec.

        install version of node  # noqa: E501

        :param version: The version of this NodeSpec.  # noqa: E501
        :type: str
        """

        self._version = version

    @property
    def ip(self):
        """Gets the ip of this NodeSpec.  # noqa: E501

        node ip address  # noqa: E501

        :return: The ip of this NodeSpec.  # noqa: E501
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip):
        """Sets the ip of this NodeSpec.

        node ip address  # noqa: E501

        :param ip: The ip of this NodeSpec.  # noqa: E501
        :type: str
        """

        self._ip = ip

    @property
    def root_user(self):
        """Gets the root_user of this NodeSpec.  # noqa: E501


        :return: The root_user of this NodeSpec.  # noqa: E501
        :rtype: str
        """
        return self._root_user

    @root_user.setter
    def root_user(self, root_user):
        """Sets the root_user of this NodeSpec.


        :param root_user: The root_user of this NodeSpec.  # noqa: E501
        :type: str
        """

        self._root_user = root_user

    @property
    def root_password(self):
        """Gets the root_password of this NodeSpec.  # noqa: E501


        :return: The root_password of this NodeSpec.  # noqa: E501
        :rtype: str
        """
        return self._root_password

    @root_password.setter
    def root_password(self, root_password):
        """Sets the root_password of this NodeSpec.


        :param root_password: The root_password of this NodeSpec.  # noqa: E501
        :type: str
        """

        self._root_password = root_password

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
        if issubclass(NodeSpec, dict):
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
        if not isinstance(other, NodeSpec):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
