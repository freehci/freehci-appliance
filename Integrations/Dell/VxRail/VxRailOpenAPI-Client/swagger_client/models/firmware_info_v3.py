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

class FirmwareInfoV3(object):
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
        'bios_revision': 'str',
        'bmc_revision': 'str',
        'hba_version': 'str',
        'expander_bpf_version': 'str',
        'nonexpander_bpf_version': 'str',
        'boss_version': 'str',
        'cpld_version': 'str',
        'idsdm_version': 'str',
        'dcpm_version': 'str',
        'perc_version': 'str'
    }

    attribute_map = {
        'bios_revision': 'bios_revision',
        'bmc_revision': 'bmc_revision',
        'hba_version': 'hba_version',
        'expander_bpf_version': 'expander_bpf_version',
        'nonexpander_bpf_version': 'nonexpander_bpf_version',
        'boss_version': 'boss_version',
        'cpld_version': 'cpld_version',
        'idsdm_version': 'idsdm_version',
        'dcpm_version': 'dcpm_version',
        'perc_version': 'perc_version'
    }

    def __init__(self, bios_revision=None, bmc_revision=None, hba_version=None, expander_bpf_version=None, nonexpander_bpf_version=None, boss_version=None, cpld_version=None, idsdm_version=None, dcpm_version=None, perc_version=None):  # noqa: E501
        """FirmwareInfoV3 - a model defined in Swagger"""  # noqa: E501
        self._bios_revision = None
        self._bmc_revision = None
        self._hba_version = None
        self._expander_bpf_version = None
        self._nonexpander_bpf_version = None
        self._boss_version = None
        self._cpld_version = None
        self._idsdm_version = None
        self._dcpm_version = None
        self._perc_version = None
        self.discriminator = None
        if bios_revision is not None:
            self.bios_revision = bios_revision
        if bmc_revision is not None:
            self.bmc_revision = bmc_revision
        if hba_version is not None:
            self.hba_version = hba_version
        if expander_bpf_version is not None:
            self.expander_bpf_version = expander_bpf_version
        if nonexpander_bpf_version is not None:
            self.nonexpander_bpf_version = nonexpander_bpf_version
        if boss_version is not None:
            self.boss_version = boss_version
        if cpld_version is not None:
            self.cpld_version = cpld_version
        if idsdm_version is not None:
            self.idsdm_version = idsdm_version
        if dcpm_version is not None:
            self.dcpm_version = dcpm_version
        if perc_version is not None:
            self.perc_version = perc_version

    @property
    def bios_revision(self):
        """Gets the bios_revision of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the BIOS.  # noqa: E501

        :return: The bios_revision of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._bios_revision

    @bios_revision.setter
    def bios_revision(self, bios_revision):
        """Sets the bios_revision of this FirmwareInfoV3.

        Firmware version of the BIOS.  # noqa: E501

        :param bios_revision: The bios_revision of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._bios_revision = bios_revision

    @property
    def bmc_revision(self):
        """Gets the bmc_revision of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the baseboard management controller (BMC).  # noqa: E501

        :return: The bmc_revision of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._bmc_revision

    @bmc_revision.setter
    def bmc_revision(self, bmc_revision):
        """Sets the bmc_revision of this FirmwareInfoV3.

        Firmware version of the baseboard management controller (BMC).  # noqa: E501

        :param bmc_revision: The bmc_revision of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._bmc_revision = bmc_revision

    @property
    def hba_version(self):
        """Gets the hba_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the host bus adapter (HBA).  # noqa: E501

        :return: The hba_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._hba_version

    @hba_version.setter
    def hba_version(self, hba_version):
        """Sets the hba_version of this FirmwareInfoV3.

        Firmware version of the host bus adapter (HBA).  # noqa: E501

        :param hba_version: The hba_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._hba_version = hba_version

    @property
    def expander_bpf_version(self):
        """Gets the expander_bpf_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the expander backplane.  # noqa: E501

        :return: The expander_bpf_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._expander_bpf_version

    @expander_bpf_version.setter
    def expander_bpf_version(self, expander_bpf_version):
        """Sets the expander_bpf_version of this FirmwareInfoV3.

        Firmware version of the expander backplane.  # noqa: E501

        :param expander_bpf_version: The expander_bpf_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._expander_bpf_version = expander_bpf_version

    @property
    def nonexpander_bpf_version(self):
        """Gets the nonexpander_bpf_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the non-expander storage backplane.  # noqa: E501

        :return: The nonexpander_bpf_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._nonexpander_bpf_version

    @nonexpander_bpf_version.setter
    def nonexpander_bpf_version(self, nonexpander_bpf_version):
        """Sets the nonexpander_bpf_version of this FirmwareInfoV3.

        Firmware version of the non-expander storage backplane.  # noqa: E501

        :param nonexpander_bpf_version: The nonexpander_bpf_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._nonexpander_bpf_version = nonexpander_bpf_version

    @property
    def boss_version(self):
        """Gets the boss_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the BOSS card.  # noqa: E501

        :return: The boss_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._boss_version

    @boss_version.setter
    def boss_version(self, boss_version):
        """Sets the boss_version of this FirmwareInfoV3.

        Firmware version of the BOSS card.  # noqa: E501

        :param boss_version: The boss_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._boss_version = boss_version

    @property
    def cpld_version(self):
        """Gets the cpld_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the complex logical device (CPLD).  # noqa: E501

        :return: The cpld_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._cpld_version

    @cpld_version.setter
    def cpld_version(self, cpld_version):
        """Sets the cpld_version of this FirmwareInfoV3.

        Firmware version of the complex logical device (CPLD).  # noqa: E501

        :param cpld_version: The cpld_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._cpld_version = cpld_version

    @property
    def idsdm_version(self):
        """Gets the idsdm_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the IDSDM.  # noqa: E501

        :return: The idsdm_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._idsdm_version

    @idsdm_version.setter
    def idsdm_version(self, idsdm_version):
        """Sets the idsdm_version of this FirmwareInfoV3.

        Firmware version of the IDSDM.  # noqa: E501

        :param idsdm_version: The idsdm_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._idsdm_version = idsdm_version

    @property
    def dcpm_version(self):
        """Gets the dcpm_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of the DC Persistent Memory (DCPM).  # noqa: E501

        :return: The dcpm_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._dcpm_version

    @dcpm_version.setter
    def dcpm_version(self, dcpm_version):
        """Sets the dcpm_version of this FirmwareInfoV3.

        Firmware version of the DC Persistent Memory (DCPM).  # noqa: E501

        :param dcpm_version: The dcpm_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._dcpm_version = dcpm_version

    @property
    def perc_version(self):
        """Gets the perc_version of this FirmwareInfoV3.  # noqa: E501

        Firmware version of PERC.  # noqa: E501

        :return: The perc_version of this FirmwareInfoV3.  # noqa: E501
        :rtype: str
        """
        return self._perc_version

    @perc_version.setter
    def perc_version(self, perc_version):
        """Sets the perc_version of this FirmwareInfoV3.

        Firmware version of PERC.  # noqa: E501

        :param perc_version: The perc_version of this FirmwareInfoV3.  # noqa: E501
        :type: str
        """

        self._perc_version = perc_version

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
        if issubclass(FirmwareInfoV3, dict):
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
        if not isinstance(other, FirmwareInfoV3):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
