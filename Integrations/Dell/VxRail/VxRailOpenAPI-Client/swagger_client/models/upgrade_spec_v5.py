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

class UpgradeSpecV5(object):
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
        'bundle_file_locator': 'str',
        'vxrail': 'VxRailManagerSpec',
        'vcenter': 'VcenterEmbeddedPSCSpecV4',
        'witness': 'WitnessSpec',
        'upgrade_sequence': 'UpgradeSequence',
        'target_hosts': 'list[HostBaseSpec]',
        'update_rules': 'UpgradeSpecV5UpdateRules'
    }

    attribute_map = {
        'bundle_file_locator': 'bundle_file_locator',
        'vxrail': 'vxrail',
        'vcenter': 'vcenter',
        'witness': 'witness',
        'upgrade_sequence': 'upgrade_sequence',
        'target_hosts': 'target_hosts',
        'update_rules': 'update_rules'
    }

    def __init__(self, bundle_file_locator=None, vxrail=None, vcenter=None, witness=None, upgrade_sequence=None, target_hosts=None, update_rules=None):  # noqa: E501
        """UpgradeSpecV5 - a model defined in Swagger"""  # noqa: E501
        self._bundle_file_locator = None
        self._vxrail = None
        self._vcenter = None
        self._witness = None
        self._upgrade_sequence = None
        self._target_hosts = None
        self._update_rules = None
        self.discriminator = None
        self.bundle_file_locator = bundle_file_locator
        self.vxrail = vxrail
        self.vcenter = vcenter
        if witness is not None:
            self.witness = witness
        if upgrade_sequence is not None:
            self.upgrade_sequence = upgrade_sequence
        if target_hosts is not None:
            self.target_hosts = target_hosts
        if update_rules is not None:
            self.update_rules = update_rules

    @property
    def bundle_file_locator(self):
        """Gets the bundle_file_locator of this UpgradeSpecV5.  # noqa: E501

        The full path of the single upgrade bundle or first package of a multiple part upgrade bundle. Multiple part upgrades must follow the mentioned criteria -- (1) The first file (the installer file) contains \"installer\" in the name. (2) Do not rename any files belonging to the multiple part bundle.  # noqa: E501

        :return: The bundle_file_locator of this UpgradeSpecV5.  # noqa: E501
        :rtype: str
        """
        return self._bundle_file_locator

    @bundle_file_locator.setter
    def bundle_file_locator(self, bundle_file_locator):
        """Sets the bundle_file_locator of this UpgradeSpecV5.

        The full path of the single upgrade bundle or first package of a multiple part upgrade bundle. Multiple part upgrades must follow the mentioned criteria -- (1) The first file (the installer file) contains \"installer\" in the name. (2) Do not rename any files belonging to the multiple part bundle.  # noqa: E501

        :param bundle_file_locator: The bundle_file_locator of this UpgradeSpecV5.  # noqa: E501
        :type: str
        """
        if bundle_file_locator is None:
            raise ValueError("Invalid value for `bundle_file_locator`, must not be `None`")  # noqa: E501

        self._bundle_file_locator = bundle_file_locator

    @property
    def vxrail(self):
        """Gets the vxrail of this UpgradeSpecV5.  # noqa: E501


        :return: The vxrail of this UpgradeSpecV5.  # noqa: E501
        :rtype: VxRailManagerSpec
        """
        return self._vxrail

    @vxrail.setter
    def vxrail(self, vxrail):
        """Sets the vxrail of this UpgradeSpecV5.


        :param vxrail: The vxrail of this UpgradeSpecV5.  # noqa: E501
        :type: VxRailManagerSpec
        """
        if vxrail is None:
            raise ValueError("Invalid value for `vxrail`, must not be `None`")  # noqa: E501

        self._vxrail = vxrail

    @property
    def vcenter(self):
        """Gets the vcenter of this UpgradeSpecV5.  # noqa: E501


        :return: The vcenter of this UpgradeSpecV5.  # noqa: E501
        :rtype: VcenterEmbeddedPSCSpecV4
        """
        return self._vcenter

    @vcenter.setter
    def vcenter(self, vcenter):
        """Sets the vcenter of this UpgradeSpecV5.


        :param vcenter: The vcenter of this UpgradeSpecV5.  # noqa: E501
        :type: VcenterEmbeddedPSCSpecV4
        """
        if vcenter is None:
            raise ValueError("Invalid value for `vcenter`, must not be `None`")  # noqa: E501

        self._vcenter = vcenter

    @property
    def witness(self):
        """Gets the witness of this UpgradeSpecV5.  # noqa: E501


        :return: The witness of this UpgradeSpecV5.  # noqa: E501
        :rtype: WitnessSpec
        """
        return self._witness

    @witness.setter
    def witness(self, witness):
        """Sets the witness of this UpgradeSpecV5.


        :param witness: The witness of this UpgradeSpecV5.  # noqa: E501
        :type: WitnessSpec
        """

        self._witness = witness

    @property
    def upgrade_sequence(self):
        """Gets the upgrade_sequence of this UpgradeSpecV5.  # noqa: E501


        :return: The upgrade_sequence of this UpgradeSpecV5.  # noqa: E501
        :rtype: UpgradeSequence
        """
        return self._upgrade_sequence

    @upgrade_sequence.setter
    def upgrade_sequence(self, upgrade_sequence):
        """Sets the upgrade_sequence of this UpgradeSpecV5.


        :param upgrade_sequence: The upgrade_sequence of this UpgradeSpecV5.  # noqa: E501
        :type: UpgradeSequence
        """

        self._upgrade_sequence = upgrade_sequence

    @property
    def target_hosts(self):
        """Gets the target_hosts of this UpgradeSpecV5.  # noqa: E501

        (Optional) Hosts to be upgraded. The target_hosts object only applies to a cluster when vLCM is enabled.  # noqa: E501

        :return: The target_hosts of this UpgradeSpecV5.  # noqa: E501
        :rtype: list[HostBaseSpec]
        """
        return self._target_hosts

    @target_hosts.setter
    def target_hosts(self, target_hosts):
        """Sets the target_hosts of this UpgradeSpecV5.

        (Optional) Hosts to be upgraded. The target_hosts object only applies to a cluster when vLCM is enabled.  # noqa: E501

        :param target_hosts: The target_hosts of this UpgradeSpecV5.  # noqa: E501
        :type: list[HostBaseSpec]
        """

        self._target_hosts = target_hosts

    @property
    def update_rules(self):
        """Gets the update_rules of this UpgradeSpecV5.  # noqa: E501


        :return: The update_rules of this UpgradeSpecV5.  # noqa: E501
        :rtype: UpgradeSpecV5UpdateRules
        """
        return self._update_rules

    @update_rules.setter
    def update_rules(self, update_rules):
        """Sets the update_rules of this UpgradeSpecV5.


        :param update_rules: The update_rules of this UpgradeSpecV5.  # noqa: E501
        :type: UpgradeSpecV5UpdateRules
        """

        self._update_rules = update_rules

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
        if issubclass(UpgradeSpecV5, dict):
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
        if not isinstance(other, UpgradeSpecV5):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
