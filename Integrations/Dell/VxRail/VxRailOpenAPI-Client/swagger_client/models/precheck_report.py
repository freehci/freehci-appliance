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

class PrecheckReport(object):
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
        'profile': 'str',
        'status': 'str',
        'progress': 'str',
        'total_severity': 'str',
        'complete_check_count': 'int',
        'total_success_count': 'int',
        'total_warn_count': 'int',
        'total_error_count': 'int',
        'results': 'PrecheckReportItem'
    }

    attribute_map = {
        'id': 'id',
        'profile': 'profile',
        'status': 'status',
        'progress': 'progress',
        'total_severity': 'total_severity',
        'complete_check_count': 'complete_check_count',
        'total_success_count': 'total_success_count',
        'total_warn_count': 'total_warn_count',
        'total_error_count': 'total_error_count',
        'results': 'results'
    }

    def __init__(self, id=None, profile=None, status=None, progress=None, total_severity=None, complete_check_count=None, total_success_count=None, total_warn_count=None, total_error_count=None, results=None):  # noqa: E501
        """PrecheckReport - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._profile = None
        self._status = None
        self._progress = None
        self._total_severity = None
        self._complete_check_count = None
        self._total_success_count = None
        self._total_warn_count = None
        self._total_error_count = None
        self._results = None
        self.discriminator = None
        if id is not None:
            self.id = id
        if profile is not None:
            self.profile = profile
        if status is not None:
            self.status = status
        if progress is not None:
            self.progress = progress
        if total_severity is not None:
            self.total_severity = total_severity
        if complete_check_count is not None:
            self.complete_check_count = complete_check_count
        if total_success_count is not None:
            self.total_success_count = total_success_count
        if total_warn_count is not None:
            self.total_warn_count = total_warn_count
        if total_error_count is not None:
            self.total_error_count = total_error_count
        if results is not None:
            self.results = results

    @property
    def id(self):
        """Gets the id of this PrecheckReport.  # noqa: E501

        Request ID (request_id) of the pre-check operation  # noqa: E501

        :return: The id of this PrecheckReport.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this PrecheckReport.

        Request ID (request_id) of the pre-check operation  # noqa: E501

        :param id: The id of this PrecheckReport.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def profile(self):
        """Gets the profile of this PrecheckReport.  # noqa: E501

        profile name  # noqa: E501

        :return: The profile of this PrecheckReport.  # noqa: E501
        :rtype: str
        """
        return self._profile

    @profile.setter
    def profile(self, profile):
        """Sets the profile of this PrecheckReport.

        profile name  # noqa: E501

        :param profile: The profile of this PrecheckReport.  # noqa: E501
        :type: str
        """

        self._profile = profile

    @property
    def status(self):
        """Gets the status of this PrecheckReport.  # noqa: E501

        Pre-check status  # noqa: E501

        :return: The status of this PrecheckReport.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this PrecheckReport.

        Pre-check status  # noqa: E501

        :param status: The status of this PrecheckReport.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def progress(self):
        """Gets the progress of this PrecheckReport.  # noqa: E501

        Pre-check progress  # noqa: E501

        :return: The progress of this PrecheckReport.  # noqa: E501
        :rtype: str
        """
        return self._progress

    @progress.setter
    def progress(self, progress):
        """Sets the progress of this PrecheckReport.

        Pre-check progress  # noqa: E501

        :param progress: The progress of this PrecheckReport.  # noqa: E501
        :type: str
        """

        self._progress = progress

    @property
    def total_severity(self):
        """Gets the total_severity of this PrecheckReport.  # noqa: E501

        Severity level of the pre-check status  # noqa: E501

        :return: The total_severity of this PrecheckReport.  # noqa: E501
        :rtype: str
        """
        return self._total_severity

    @total_severity.setter
    def total_severity(self, total_severity):
        """Sets the total_severity of this PrecheckReport.

        Severity level of the pre-check status  # noqa: E501

        :param total_severity: The total_severity of this PrecheckReport.  # noqa: E501
        :type: str
        """

        self._total_severity = total_severity

    @property
    def complete_check_count(self):
        """Gets the complete_check_count of this PrecheckReport.  # noqa: E501

        Number of pre-check tasks completed  # noqa: E501

        :return: The complete_check_count of this PrecheckReport.  # noqa: E501
        :rtype: int
        """
        return self._complete_check_count

    @complete_check_count.setter
    def complete_check_count(self, complete_check_count):
        """Sets the complete_check_count of this PrecheckReport.

        Number of pre-check tasks completed  # noqa: E501

        :param complete_check_count: The complete_check_count of this PrecheckReport.  # noqa: E501
        :type: int
        """

        self._complete_check_count = complete_check_count

    @property
    def total_success_count(self):
        """Gets the total_success_count of this PrecheckReport.  # noqa: E501

        Number of pre-check tasks successfully completed  # noqa: E501

        :return: The total_success_count of this PrecheckReport.  # noqa: E501
        :rtype: int
        """
        return self._total_success_count

    @total_success_count.setter
    def total_success_count(self, total_success_count):
        """Sets the total_success_count of this PrecheckReport.

        Number of pre-check tasks successfully completed  # noqa: E501

        :param total_success_count: The total_success_count of this PrecheckReport.  # noqa: E501
        :type: int
        """

        self._total_success_count = total_success_count

    @property
    def total_warn_count(self):
        """Gets the total_warn_count of this PrecheckReport.  # noqa: E501

        Total number of pre-check warnings  # noqa: E501

        :return: The total_warn_count of this PrecheckReport.  # noqa: E501
        :rtype: int
        """
        return self._total_warn_count

    @total_warn_count.setter
    def total_warn_count(self, total_warn_count):
        """Sets the total_warn_count of this PrecheckReport.

        Total number of pre-check warnings  # noqa: E501

        :param total_warn_count: The total_warn_count of this PrecheckReport.  # noqa: E501
        :type: int
        """

        self._total_warn_count = total_warn_count

    @property
    def total_error_count(self):
        """Gets the total_error_count of this PrecheckReport.  # noqa: E501

        Total number of pre-check errors  # noqa: E501

        :return: The total_error_count of this PrecheckReport.  # noqa: E501
        :rtype: int
        """
        return self._total_error_count

    @total_error_count.setter
    def total_error_count(self, total_error_count):
        """Sets the total_error_count of this PrecheckReport.

        Total number of pre-check errors  # noqa: E501

        :param total_error_count: The total_error_count of this PrecheckReport.  # noqa: E501
        :type: int
        """

        self._total_error_count = total_error_count

    @property
    def results(self):
        """Gets the results of this PrecheckReport.  # noqa: E501


        :return: The results of this PrecheckReport.  # noqa: E501
        :rtype: PrecheckReportItem
        """
        return self._results

    @results.setter
    def results(self, results):
        """Sets the results of this PrecheckReport.


        :param results: The results of this PrecheckReport.  # noqa: E501
        :type: PrecheckReportItem
        """

        self._results = results

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
        if issubclass(PrecheckReport, dict):
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
        if not isinstance(other, PrecheckReport):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
