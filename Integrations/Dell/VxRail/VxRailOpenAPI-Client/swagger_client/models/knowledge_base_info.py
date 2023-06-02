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

class KnowledgeBaseInfo(object):
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
        'home_url': 'str',
        'articles_link': 'str'
    }

    attribute_map = {
        'home_url': 'homeURL',
        'articles_link': 'articlesLink'
    }

    def __init__(self, home_url=None, articles_link=None):  # noqa: E501
        """KnowledgeBaseInfo - a model defined in Swagger"""  # noqa: E501
        self._home_url = None
        self._articles_link = None
        self.discriminator = None
        self.home_url = home_url
        if articles_link is not None:
            self.articles_link = articles_link

    @property
    def home_url(self):
        """Gets the home_url of this KnowledgeBaseInfo.  # noqa: E501

        The home URL of the VxRail Support Knowledge Base  # noqa: E501

        :return: The home_url of this KnowledgeBaseInfo.  # noqa: E501
        :rtype: str
        """
        return self._home_url

    @home_url.setter
    def home_url(self, home_url):
        """Sets the home_url of this KnowledgeBaseInfo.

        The home URL of the VxRail Support Knowledge Base  # noqa: E501

        :param home_url: The home_url of this KnowledgeBaseInfo.  # noqa: E501
        :type: str
        """
        if home_url is None:
            raise ValueError("Invalid value for `home_url`, must not be `None`")  # noqa: E501

        self._home_url = home_url

    @property
    def articles_link(self):
        """Gets the articles_link of this KnowledgeBaseInfo.  # noqa: E501

        The link for retrieving KB articles  # noqa: E501

        :return: The articles_link of this KnowledgeBaseInfo.  # noqa: E501
        :rtype: str
        """
        return self._articles_link

    @articles_link.setter
    def articles_link(self, articles_link):
        """Sets the articles_link of this KnowledgeBaseInfo.

        The link for retrieving KB articles  # noqa: E501

        :param articles_link: The articles_link of this KnowledgeBaseInfo.  # noqa: E501
        :type: str
        """

        self._articles_link = articles_link

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
        if issubclass(KnowledgeBaseInfo, dict):
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
        if not isinstance(other, KnowledgeBaseInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
