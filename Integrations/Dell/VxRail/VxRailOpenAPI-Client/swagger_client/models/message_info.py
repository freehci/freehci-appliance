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

class MessageInfo(object):
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
        'type': 'str',
        'title': 'str',
        'url': 'str',
        'author': 'str',
        '_date': 'int',
        'tags': 'list[str]',
        'status': 'str',
        'view_count': 'int',
        'reply_count': 'int',
        'resolved': 'str'
    }

    attribute_map = {
        'id': 'id',
        'type': 'type',
        'title': 'title',
        'url': 'url',
        'author': 'author',
        '_date': 'date',
        'tags': 'tags',
        'status': 'status',
        'view_count': 'viewCount',
        'reply_count': 'replyCount',
        'resolved': 'resolved'
    }

    def __init__(self, id=None, type=None, title=None, url=None, author=None, _date=None, tags=None, status=None, view_count=None, reply_count=None, resolved=None):  # noqa: E501
        """MessageInfo - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._type = None
        self._title = None
        self._url = None
        self._author = None
        self.__date = None
        self._tags = None
        self._status = None
        self._view_count = None
        self._reply_count = None
        self._resolved = None
        self.discriminator = None
        self.id = id
        self.type = type
        self.title = title
        self.url = url
        self.author = author
        self._date = _date
        if tags is not None:
            self.tags = tags
        if status is not None:
            self.status = status
        if view_count is not None:
            self.view_count = view_count
        if reply_count is not None:
            self.reply_count = reply_count
        if resolved is not None:
            self.resolved = resolved

    @property
    def id(self):
        """Gets the id of this MessageInfo.  # noqa: E501

        ID of the message  # noqa: E501

        :return: The id of this MessageInfo.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this MessageInfo.

        ID of the message  # noqa: E501

        :param id: The id of this MessageInfo.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def type(self):
        """Gets the type of this MessageInfo.  # noqa: E501

        Type of the message  # noqa: E501

        :return: The type of this MessageInfo.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this MessageInfo.

        Type of the message  # noqa: E501

        :param type: The type of this MessageInfo.  # noqa: E501
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def title(self):
        """Gets the title of this MessageInfo.  # noqa: E501

        Title of the message  # noqa: E501

        :return: The title of this MessageInfo.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this MessageInfo.

        Title of the message  # noqa: E501

        :param title: The title of this MessageInfo.  # noqa: E501
        :type: str
        """
        if title is None:
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def url(self):
        """Gets the url of this MessageInfo.  # noqa: E501

        URL of the message  # noqa: E501

        :return: The url of this MessageInfo.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this MessageInfo.

        URL of the message  # noqa: E501

        :param url: The url of this MessageInfo.  # noqa: E501
        :type: str
        """
        if url is None:
            raise ValueError("Invalid value for `url`, must not be `None`")  # noqa: E501

        self._url = url

    @property
    def author(self):
        """Gets the author of this MessageInfo.  # noqa: E501

        Author of the message  # noqa: E501

        :return: The author of this MessageInfo.  # noqa: E501
        :rtype: str
        """
        return self._author

    @author.setter
    def author(self, author):
        """Sets the author of this MessageInfo.

        Author of the message  # noqa: E501

        :param author: The author of this MessageInfo.  # noqa: E501
        :type: str
        """
        if author is None:
            raise ValueError("Invalid value for `author`, must not be `None`")  # noqa: E501

        self._author = author

    @property
    def _date(self):
        """Gets the _date of this MessageInfo.  # noqa: E501

        Date that the message was posted  # noqa: E501

        :return: The _date of this MessageInfo.  # noqa: E501
        :rtype: int
        """
        return self.__date

    @_date.setter
    def _date(self, _date):
        """Sets the _date of this MessageInfo.

        Date that the message was posted  # noqa: E501

        :param _date: The _date of this MessageInfo.  # noqa: E501
        :type: int
        """
        if _date is None:
            raise ValueError("Invalid value for `_date`, must not be `None`")  # noqa: E501

        self.__date = _date

    @property
    def tags(self):
        """Gets the tags of this MessageInfo.  # noqa: E501

        Informational tags about the message  # noqa: E501

        :return: The tags of this MessageInfo.  # noqa: E501
        :rtype: list[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this MessageInfo.

        Informational tags about the message  # noqa: E501

        :param tags: The tags of this MessageInfo.  # noqa: E501
        :type: list[str]
        """

        self._tags = tags

    @property
    def status(self):
        """Gets the status of this MessageInfo.  # noqa: E501

        Status of the message  # noqa: E501

        :return: The status of this MessageInfo.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this MessageInfo.

        Status of the message  # noqa: E501

        :param status: The status of this MessageInfo.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def view_count(self):
        """Gets the view_count of this MessageInfo.  # noqa: E501

        How many times the message has been viewed  # noqa: E501

        :return: The view_count of this MessageInfo.  # noqa: E501
        :rtype: int
        """
        return self._view_count

    @view_count.setter
    def view_count(self, view_count):
        """Sets the view_count of this MessageInfo.

        How many times the message has been viewed  # noqa: E501

        :param view_count: The view_count of this MessageInfo.  # noqa: E501
        :type: int
        """

        self._view_count = view_count

    @property
    def reply_count(self):
        """Gets the reply_count of this MessageInfo.  # noqa: E501

        The number of comments posted on the message  # noqa: E501

        :return: The reply_count of this MessageInfo.  # noqa: E501
        :rtype: int
        """
        return self._reply_count

    @reply_count.setter
    def reply_count(self, reply_count):
        """Sets the reply_count of this MessageInfo.

        The number of comments posted on the message  # noqa: E501

        :param reply_count: The reply_count of this MessageInfo.  # noqa: E501
        :type: int
        """

        self._reply_count = reply_count

    @property
    def resolved(self):
        """Gets the resolved of this MessageInfo.  # noqa: E501

        The resolve status of message  # noqa: E501

        :return: The resolved of this MessageInfo.  # noqa: E501
        :rtype: str
        """
        return self._resolved

    @resolved.setter
    def resolved(self, resolved):
        """Sets the resolved of this MessageInfo.

        The resolve status of message  # noqa: E501

        :param resolved: The resolved of this MessageInfo.  # noqa: E501
        :type: str
        """

        self._resolved = resolved

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
        if issubclass(MessageInfo, dict):
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
        if not isinstance(other, MessageInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
