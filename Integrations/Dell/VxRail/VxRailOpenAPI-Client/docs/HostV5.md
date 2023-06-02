# HostV5

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID number of the host | [optional] 
**sn** | **str** | Serial number of the host | [optional] 
**type** | **str** | Node type | [optional] 
**slot** | **int** | Rack slot position where the VxRail host appliance is installed | [optional] 
**hostname** | **str** | Hostname of the host | [optional] 
**name** | **str** | Name of the host | [optional] 
**manufacturer** | **str** | Manufacturer of the host | [optional] 
**psnt** | **str** | Product serial number tag (PSNT) of the host | [optional] 
**led_status** | **str** | State of the chassis LED indicator for the host | [optional] 
**health** | **str** | Health status of the VxRail system. Supported values are Critical, Error, Warning, and Healthy | [optional] 
**missing** | **bool** | Whether the chassis health status is critical. Supported values are false (not critical) and true (critical) | [optional] 
**tpm_present** | **bool** | Whether a TPM security device is installed on the VxRail host | [optional] 
**operational_status** | **str** | Operational status of the host | [optional] 
**power_status** | **str** | Power supply status of the host | [optional] 
**boot_devices** | [**list[BootDeviceV2]**](BootDeviceV2.md) |  | [optional] 
**nics** | [**list[Nic]**](Nic.md) |  | [optional] 
**disks** | [**list[DiskInfoV2]**](DiskInfoV2.md) |  | [optional] 
**firmware_info** | [**FirmwareInfoV3**](FirmwareInfoV3.md) |  | [optional] 
**geo_location** | [**GeoLocation**](GeoLocation.md) |  | [optional] 
**drive_configuration** | [**DriveConfigurationInfo**](DriveConfigurationInfo.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

