# Host

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID number of the host | [optional] 
**sn** | **str** | Serial number of the host | [optional] 
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
**boot_devices** | [**list[BootDevice]**](BootDevice.md) |  | [optional] 
**nics** | [**list[Nic]**](Nic.md) |  | [optional] 
**disks** | [**list[DiskInfo]**](DiskInfo.md) |  | [optional] 
**firmware_info** | [**FirmwareInfo**](FirmwareInfo.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

