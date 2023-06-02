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

class SystemValidatecredentialBody(object):
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
        'vxrail': 'VxRailCredential',
        'vcenter': 'VcenterCredential',
        'hosts': 'list[EsxiHostCredential]',
        'witness_user': 'WitnessNodeCredential'
    }

    attribute_map = {
        'vxrail': 'vxrail',
        'vcenter': 'vcenter',
        'hosts': 'hosts',
        'witness_user': 'witness-user'
    }

    def __init__(self, vxrail=None, vcenter=None, hosts=None, witness_user=None):  # noqa: E501
        """SystemValidatecredentialBody - a model defined in Swagger"""  # noqa: E501
        self._vxrail = None
        self._vcenter = None
        self._hosts = None
        self._witness_user = None
        self.discriminator = None
        if vxrail is not None:
            self.vxrail = vxrail
        if vcenter is not None:
            self.vcenter = vcenter
        if hosts is not None:
            self.hosts = hosts
        if witness_user is not None:
            self.witness_user = witness_user

    @property
    def vxrail(self):
        """Gets the vxrail of this SystemValidatecredentialBody.  # noqa: E501


        :return: The vxrail of this SystemValidatecredentialBody.  # noqa: E501
        :rtype: VxRailCredential
        """
        return self._vxrail

    @vxrail.setter
    def vxrail(self, vxrail):
        """Sets the vxrail of this SystemValidatecredentialBody.


        :param vxrail: The vxrail of this SystemValidatecredentialBody.  # noqa: E501
        :type: VxRailCredential
        """

        self._vxrail = vxrail

    @property
    def vcenter(self):
        """Gets the vcenter of this SystemValidatecredentialBody.  # noqa: E501


        :return: The vcenter of this SystemValidatecredentialBody.  # noqa: E501
        :rtype: VcenterCredential
        """
        return self._vcenter

    @vcenter.setter
    def vcenter(self, vcenter):
        """Sets the vcenter of this SystemValidatecredentialBody.


        :param vcenter: The vcenter of this SystemValidatecredentialBody.  # noqa: E501
        :type: VcenterCredential
        """

        self._vcenter = vcenter

    @property
    def hosts(self):
        """Gets the hosts of this SystemValidatecredentialBody.  # noqa: E501

        Information regarding credentials and serial numbers for the ESXi hosts.  # noqa: E501

        :return: The hosts of this SystemValidatecredentialBody.  # noqa: E501
        :rtype: list[EsxiHostCredential]
        """
        return self._hosts

    @hosts.setter
    def hosts(self, hosts):
        """Sets the hosts of this SystemValidatecredentialBody.

        Information regarding credentials and serial numbers for the ESXi hosts.  # noqa: E501

        :param hosts: The hosts of this SystemValidatecredentialBody.  # noqa: E501
        :type: list[EsxiHostCredential]
        """

        self._hosts = hosts

    @property
    def witness_user(self):
        """Gets the witness_user of this SystemValidatecredentialBody.  # noqa: E501


        :return: The witness_user of this SystemValidatecredentialBody.  # noqa: E501
        :rtype: WitnessNodeCredential
        """
        return self._witness_user

    @witness_user.setter
    def witness_user(self, witness_user):
        """Sets the witness_user of this SystemValidatecredentialBody.


        :param witness_user: The witness_user of this SystemValidatecredentialBody.  # noqa: E501
        :type: WitnessNodeCredential
        """

        self._witness_user = witness_user

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
        if issubclass(SystemValidatecredentialBody, dict):
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
        if not isinstance(other, SystemValidatecredentialBody):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
