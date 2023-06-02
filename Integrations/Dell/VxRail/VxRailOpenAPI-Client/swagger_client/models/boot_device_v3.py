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

class BootDeviceV3(object):
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
        'sn': 'str',
        'device_model': 'str',
        'device_type': 'str',
        'protocol': 'str',
        'sata_type': 'str',
        'power_on_hours': 'int',
        'power_cycle_count': 'int',
        'max_erase_count': 'int',
        'avr_erase_count': 'int',
        'capacity': 'str',
        'health': 'str',
        'firmware_version': 'str',
        'bootdevice_type': 'str',
        'block_size': 'str',
        'slot': 'int',
        'status': 'str',
        'part_number': 'str',
        'manufacturer': 'str',
        'controller_firmware': 'str',
        'controller_model': 'str',
        'controller_status': 'str'
    }

    attribute_map = {
        'id': 'id',
        'sn': 'sn',
        'device_model': 'device_model',
        'device_type': 'device_type',
        'protocol': 'protocol',
        'sata_type': 'sata_type',
        'power_on_hours': 'power_on_hours',
        'power_cycle_count': 'power_cycle_count',
        'max_erase_count': 'max_erase_count',
        'avr_erase_count': 'avr_erase_count',
        'capacity': 'capacity',
        'health': 'health',
        'firmware_version': 'firmware_version',
        'bootdevice_type': 'bootdevice_type',
        'block_size': 'block_size',
        'slot': 'slot',
        'status': 'status',
        'part_number': 'part_number',
        'manufacturer': 'manufacturer',
        'controller_firmware': 'controller_firmware',
        'controller_model': 'controller_model',
        'controller_status': 'controller_status'
    }

    def __init__(self, id=None, sn=None, device_model=None, device_type=None, protocol=None, sata_type=None, power_on_hours=None, power_cycle_count=None, max_erase_count=None, avr_erase_count=None, capacity=None, health=None, firmware_version=None, bootdevice_type=None, block_size=None, slot=None, status=None, part_number=None, manufacturer=None, controller_firmware=None, controller_model=None, controller_status=None):  # noqa: E501
        """BootDeviceV3 - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._sn = None
        self._device_model = None
        self._device_type = None
        self._protocol = None
        self._sata_type = None
        self._power_on_hours = None
        self._power_cycle_count = None
        self._max_erase_count = None
        self._avr_erase_count = None
        self._capacity = None
        self._health = None
        self._firmware_version = None
        self._bootdevice_type = None
        self._block_size = None
        self._slot = None
        self._status = None
        self._part_number = None
        self._manufacturer = None
        self._controller_firmware = None
        self._controller_model = None
        self._controller_status = None
        self.discriminator = None
        if id is not None:
            self.id = id
        if sn is not None:
            self.sn = sn
        if device_model is not None:
            self.device_model = device_model
        if device_type is not None:
            self.device_type = device_type
        if protocol is not None:
            self.protocol = protocol
        if sata_type is not None:
            self.sata_type = sata_type
        if power_on_hours is not None:
            self.power_on_hours = power_on_hours
        if power_cycle_count is not None:
            self.power_cycle_count = power_cycle_count
        if max_erase_count is not None:
            self.max_erase_count = max_erase_count
        if avr_erase_count is not None:
            self.avr_erase_count = avr_erase_count
        if capacity is not None:
            self.capacity = capacity
        if health is not None:
            self.health = health
        if firmware_version is not None:
            self.firmware_version = firmware_version
        if bootdevice_type is not None:
            self.bootdevice_type = bootdevice_type
        if block_size is not None:
            self.block_size = block_size
        if slot is not None:
            self.slot = slot
        if status is not None:
            self.status = status
        if part_number is not None:
            self.part_number = part_number
        if manufacturer is not None:
            self.manufacturer = manufacturer
        if controller_firmware is not None:
            self.controller_firmware = controller_firmware
        if controller_model is not None:
            self.controller_model = controller_model
        if controller_status is not None:
            self.controller_status = controller_status

    @property
    def id(self):
        """Gets the id of this BootDeviceV3.  # noqa: E501

        ID of the boot device  # noqa: E501

        :return: The id of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this BootDeviceV3.

        ID of the boot device  # noqa: E501

        :param id: The id of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def sn(self):
        """Gets the sn of this BootDeviceV3.  # noqa: E501

        Serial number of the boot device  # noqa: E501

        :return: The sn of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._sn

    @sn.setter
    def sn(self, sn):
        """Sets the sn of this BootDeviceV3.

        Serial number of the boot device  # noqa: E501

        :param sn: The sn of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._sn = sn

    @property
    def device_model(self):
        """Gets the device_model of this BootDeviceV3.  # noqa: E501

        Model number of the boot device  # noqa: E501

        :return: The device_model of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._device_model

    @device_model.setter
    def device_model(self, device_model):
        """Sets the device_model of this BootDeviceV3.

        Model number of the boot device  # noqa: E501

        :param device_model: The device_model of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._device_model = device_model

    @property
    def device_type(self):
        """Gets the device_type of this BootDeviceV3.  # noqa: E501

        Model type of the boot device  # noqa: E501

        :return: The device_type of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._device_type

    @device_type.setter
    def device_type(self, device_type):
        """Sets the device_type of this BootDeviceV3.

        Model type of the boot device  # noqa: E501

        :param device_type: The device_type of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._device_type = device_type

    @property
    def protocol(self):
        """Gets the protocol of this BootDeviceV3.  # noqa: E501

        Type of transport protocol  # noqa: E501

        :return: The protocol of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """Sets the protocol of this BootDeviceV3.

        Type of transport protocol  # noqa: E501

        :param protocol: The protocol of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._protocol = protocol

    @property
    def sata_type(self):
        """Gets the sata_type of this BootDeviceV3.  # noqa: E501

        Type of disk drive of the device  # noqa: E501

        :return: The sata_type of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._sata_type

    @sata_type.setter
    def sata_type(self, sata_type):
        """Sets the sata_type of this BootDeviceV3.

        Type of disk drive of the device  # noqa: E501

        :param sata_type: The sata_type of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._sata_type = sata_type

    @property
    def power_on_hours(self):
        """Gets the power_on_hours of this BootDeviceV3.  # noqa: E501

        Number of hours the device is powered on  # noqa: E501

        :return: The power_on_hours of this BootDeviceV3.  # noqa: E501
        :rtype: int
        """
        return self._power_on_hours

    @power_on_hours.setter
    def power_on_hours(self, power_on_hours):
        """Sets the power_on_hours of this BootDeviceV3.

        Number of hours the device is powered on  # noqa: E501

        :param power_on_hours: The power_on_hours of this BootDeviceV3.  # noqa: E501
        :type: int
        """

        self._power_on_hours = power_on_hours

    @property
    def power_cycle_count(self):
        """Gets the power_cycle_count of this BootDeviceV3.  # noqa: E501

        Number of times the device is powered on and off.  # noqa: E501

        :return: The power_cycle_count of this BootDeviceV3.  # noqa: E501
        :rtype: int
        """
        return self._power_cycle_count

    @power_cycle_count.setter
    def power_cycle_count(self, power_cycle_count):
        """Sets the power_cycle_count of this BootDeviceV3.

        Number of times the device is powered on and off.  # noqa: E501

        :param power_cycle_count: The power_cycle_count of this BootDeviceV3.  # noqa: E501
        :type: int
        """

        self._power_cycle_count = power_cycle_count

    @property
    def max_erase_count(self):
        """Gets the max_erase_count of this BootDeviceV3.  # noqa: E501

        Maximum erase count for the device  # noqa: E501

        :return: The max_erase_count of this BootDeviceV3.  # noqa: E501
        :rtype: int
        """
        return self._max_erase_count

    @max_erase_count.setter
    def max_erase_count(self, max_erase_count):
        """Sets the max_erase_count of this BootDeviceV3.

        Maximum erase count for the device  # noqa: E501

        :param max_erase_count: The max_erase_count of this BootDeviceV3.  # noqa: E501
        :type: int
        """

        self._max_erase_count = max_erase_count

    @property
    def avr_erase_count(self):
        """Gets the avr_erase_count of this BootDeviceV3.  # noqa: E501

        Average erase count for the device  # noqa: E501

        :return: The avr_erase_count of this BootDeviceV3.  # noqa: E501
        :rtype: int
        """
        return self._avr_erase_count

    @avr_erase_count.setter
    def avr_erase_count(self, avr_erase_count):
        """Sets the avr_erase_count of this BootDeviceV3.

        Average erase count for the device  # noqa: E501

        :param avr_erase_count: The avr_erase_count of this BootDeviceV3.  # noqa: E501
        :type: int
        """

        self._avr_erase_count = avr_erase_count

    @property
    def capacity(self):
        """Gets the capacity of this BootDeviceV3.  # noqa: E501

        Capacity of the device disk  # noqa: E501

        :return: The capacity of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._capacity

    @capacity.setter
    def capacity(self, capacity):
        """Sets the capacity of this BootDeviceV3.

        Capacity of the device disk  # noqa: E501

        :param capacity: The capacity of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._capacity = capacity

    @property
    def health(self):
        """Gets the health of this BootDeviceV3.  # noqa: E501

        Health status of the boot device (percentage)  # noqa: E501

        :return: The health of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._health

    @health.setter
    def health(self, health):
        """Sets the health of this BootDeviceV3.

        Health status of the boot device (percentage)  # noqa: E501

        :param health: The health of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._health = health

    @property
    def firmware_version(self):
        """Gets the firmware_version of this BootDeviceV3.  # noqa: E501

        Firmware version of the boot device.  # noqa: E501

        :return: The firmware_version of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._firmware_version

    @firmware_version.setter
    def firmware_version(self, firmware_version):
        """Sets the firmware_version of this BootDeviceV3.

        Firmware version of the boot device.  # noqa: E501

        :param firmware_version: The firmware_version of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._firmware_version = firmware_version

    @property
    def bootdevice_type(self):
        """Gets the bootdevice_type of this BootDeviceV3.  # noqa: E501

        Type of boot device  # noqa: E501

        :return: The bootdevice_type of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._bootdevice_type

    @bootdevice_type.setter
    def bootdevice_type(self, bootdevice_type):
        """Sets the bootdevice_type of this BootDeviceV3.

        Type of boot device  # noqa: E501

        :param bootdevice_type: The bootdevice_type of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._bootdevice_type = bootdevice_type

    @property
    def block_size(self):
        """Gets the block_size of this BootDeviceV3.  # noqa: E501

        Block size of the boot device  # noqa: E501

        :return: The block_size of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._block_size

    @block_size.setter
    def block_size(self, block_size):
        """Sets the block_size of this BootDeviceV3.

        Block size of the boot device  # noqa: E501

        :param block_size: The block_size of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._block_size = block_size

    @property
    def slot(self):
        """Gets the slot of this BootDeviceV3.  # noqa: E501

        Slot number of the boot device  # noqa: E501

        :return: The slot of this BootDeviceV3.  # noqa: E501
        :rtype: int
        """
        return self._slot

    @slot.setter
    def slot(self, slot):
        """Sets the slot of this BootDeviceV3.

        Slot number of the boot device  # noqa: E501

        :param slot: The slot of this BootDeviceV3.  # noqa: E501
        :type: int
        """

        self._slot = slot

    @property
    def status(self):
        """Gets the status of this BootDeviceV3.  # noqa: E501

        Status of the boot device  # noqa: E501

        :return: The status of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this BootDeviceV3.

        Status of the boot device  # noqa: E501

        :param status: The status of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def part_number(self):
        """Gets the part_number of this BootDeviceV3.  # noqa: E501

        Part number of the boot device  # noqa: E501

        :return: The part_number of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._part_number

    @part_number.setter
    def part_number(self, part_number):
        """Sets the part_number of this BootDeviceV3.

        Part number of the boot device  # noqa: E501

        :param part_number: The part_number of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._part_number = part_number

    @property
    def manufacturer(self):
        """Gets the manufacturer of this BootDeviceV3.  # noqa: E501

        Manufacturer of the boot device  # noqa: E501

        :return: The manufacturer of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, manufacturer):
        """Sets the manufacturer of this BootDeviceV3.

        Manufacturer of the boot device  # noqa: E501

        :param manufacturer: The manufacturer of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._manufacturer = manufacturer

    @property
    def controller_firmware(self):
        """Gets the controller_firmware of this BootDeviceV3.  # noqa: E501

        Controller firmware version of the boot device  # noqa: E501

        :return: The controller_firmware of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._controller_firmware

    @controller_firmware.setter
    def controller_firmware(self, controller_firmware):
        """Sets the controller_firmware of this BootDeviceV3.

        Controller firmware version of the boot device  # noqa: E501

        :param controller_firmware: The controller_firmware of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._controller_firmware = controller_firmware

    @property
    def controller_model(self):
        """Gets the controller_model of this BootDeviceV3.  # noqa: E501

        Controller model of the boot device  # noqa: E501

        :return: The controller_model of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._controller_model

    @controller_model.setter
    def controller_model(self, controller_model):
        """Sets the controller_model of this BootDeviceV3.

        Controller model of the boot device  # noqa: E501

        :param controller_model: The controller_model of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._controller_model = controller_model

    @property
    def controller_status(self):
        """Gets the controller_status of this BootDeviceV3.  # noqa: E501

        Controller status of the boot device  # noqa: E501

        :return: The controller_status of this BootDeviceV3.  # noqa: E501
        :rtype: str
        """
        return self._controller_status

    @controller_status.setter
    def controller_status(self, controller_status):
        """Sets the controller_status of this BootDeviceV3.

        Controller status of the boot device  # noqa: E501

        :param controller_status: The controller_status of this BootDeviceV3.  # noqa: E501
        :type: str
        """

        self._controller_status = controller_status

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
        if issubclass(BootDeviceV3, dict):
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
        if not isinstance(other, BootDeviceV3):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
