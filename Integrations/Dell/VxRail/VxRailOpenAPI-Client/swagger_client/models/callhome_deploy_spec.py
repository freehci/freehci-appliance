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

class CallhomeDeploySpec(object):
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
        'ip': 'str',
        'site_id': 'str',
        'first_name': 'str',
        'last_name': 'str',
        'email': 'str',
        'phone': 'str',
        'company': 'str',
        'root_pwd': 'str',
        'admin_pwd': 'str'
    }

    attribute_map = {
        'ip': 'ip',
        'site_id': 'site_id',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email',
        'phone': 'phone',
        'company': 'company',
        'root_pwd': 'root_pwd',
        'admin_pwd': 'admin_pwd'
    }

    def __init__(self, ip=None, site_id=None, first_name=None, last_name=None, email=None, phone=None, company=None, root_pwd=None, admin_pwd=None):  # noqa: E501
        """CallhomeDeploySpec - a model defined in Swagger"""  # noqa: E501
        self._ip = None
        self._site_id = None
        self._first_name = None
        self._last_name = None
        self._email = None
        self._phone = None
        self._company = None
        self._root_pwd = None
        self._admin_pwd = None
        self.discriminator = None
        self.ip = ip
        self.site_id = site_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.company = company
        self.root_pwd = root_pwd
        self.admin_pwd = admin_pwd

    @property
    def ip(self):
        """Gets the ip of this CallhomeDeploySpec.  # noqa: E501

        IP address for the SRS server  # noqa: E501

        :return: The ip of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip):
        """Sets the ip of this CallhomeDeploySpec.

        IP address for the SRS server  # noqa: E501

        :param ip: The ip of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if ip is None:
            raise ValueError("Invalid value for `ip`, must not be `None`")  # noqa: E501

        self._ip = ip

    @property
    def site_id(self):
        """Gets the site_id of this CallhomeDeploySpec.  # noqa: E501

        Site ID of the SRS server  # noqa: E501

        :return: The site_id of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._site_id

    @site_id.setter
    def site_id(self, site_id):
        """Sets the site_id of this CallhomeDeploySpec.

        Site ID of the SRS server  # noqa: E501

        :param site_id: The site_id of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if site_id is None:
            raise ValueError("Invalid value for `site_id`, must not be `None`")  # noqa: E501

        self._site_id = site_id

    @property
    def first_name(self):
        """Gets the first_name of this CallhomeDeploySpec.  # noqa: E501

        First name of the support administrator  # noqa: E501

        :return: The first_name of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        """Sets the first_name of this CallhomeDeploySpec.

        First name of the support administrator  # noqa: E501

        :param first_name: The first_name of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if first_name is None:
            raise ValueError("Invalid value for `first_name`, must not be `None`")  # noqa: E501

        self._first_name = first_name

    @property
    def last_name(self):
        """Gets the last_name of this CallhomeDeploySpec.  # noqa: E501

        Last name of the support administrator  # noqa: E501

        :return: The last_name of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._last_name

    @last_name.setter
    def last_name(self, last_name):
        """Sets the last_name of this CallhomeDeploySpec.

        Last name of the support administrator  # noqa: E501

        :param last_name: The last_name of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if last_name is None:
            raise ValueError("Invalid value for `last_name`, must not be `None`")  # noqa: E501

        self._last_name = last_name

    @property
    def email(self):
        """Gets the email of this CallhomeDeploySpec.  # noqa: E501

        Email address of the support account  # noqa: E501

        :return: The email of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this CallhomeDeploySpec.

        Email address of the support account  # noqa: E501

        :param email: The email of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if email is None:
            raise ValueError("Invalid value for `email`, must not be `None`")  # noqa: E501

        self._email = email

    @property
    def phone(self):
        """Gets the phone of this CallhomeDeploySpec.  # noqa: E501

        Phone number of the support administrator  # noqa: E501

        :return: The phone of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._phone

    @phone.setter
    def phone(self, phone):
        """Sets the phone of this CallhomeDeploySpec.

        Phone number of the support administrator  # noqa: E501

        :param phone: The phone of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if phone is None:
            raise ValueError("Invalid value for `phone`, must not be `None`")  # noqa: E501

        self._phone = phone

    @property
    def company(self):
        """Gets the company of this CallhomeDeploySpec.  # noqa: E501

        Company name  # noqa: E501

        :return: The company of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._company

    @company.setter
    def company(self, company):
        """Sets the company of this CallhomeDeploySpec.

        Company name  # noqa: E501

        :param company: The company of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if company is None:
            raise ValueError("Invalid value for `company`, must not be `None`")  # noqa: E501

        self._company = company

    @property
    def root_pwd(self):
        """Gets the root_pwd of this CallhomeDeploySpec.  # noqa: E501

        Root password for accessing the SRS server  # noqa: E501

        :return: The root_pwd of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._root_pwd

    @root_pwd.setter
    def root_pwd(self, root_pwd):
        """Sets the root_pwd of this CallhomeDeploySpec.

        Root password for accessing the SRS server  # noqa: E501

        :param root_pwd: The root_pwd of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if root_pwd is None:
            raise ValueError("Invalid value for `root_pwd`, must not be `None`")  # noqa: E501

        self._root_pwd = root_pwd

    @property
    def admin_pwd(self):
        """Gets the admin_pwd of this CallhomeDeploySpec.  # noqa: E501

        Administrator password for accessing the SRS server  # noqa: E501

        :return: The admin_pwd of this CallhomeDeploySpec.  # noqa: E501
        :rtype: str
        """
        return self._admin_pwd

    @admin_pwd.setter
    def admin_pwd(self, admin_pwd):
        """Sets the admin_pwd of this CallhomeDeploySpec.

        Administrator password for accessing the SRS server  # noqa: E501

        :param admin_pwd: The admin_pwd of this CallhomeDeploySpec.  # noqa: E501
        :type: str
        """
        if admin_pwd is None:
            raise ValueError("Invalid value for `admin_pwd`, must not be `None`")  # noqa: E501

        self._admin_pwd = admin_pwd

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
        if issubclass(CallhomeDeploySpec, dict):
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
        if not isinstance(other, CallhomeDeploySpec):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
