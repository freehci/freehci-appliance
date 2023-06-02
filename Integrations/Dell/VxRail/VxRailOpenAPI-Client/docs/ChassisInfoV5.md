# ChassisInfoV5

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the chassis | [optional] 
**sn** | **str** | Serial number of the chassis | [optional] 
**part_number** | **str** | Part number of the chassis | [optional] 
**slot** | **int** | Rack slot position where the VxRail host appliance is installed | [optional] 
**hostname** | **object** | Indicates the hostname | [optional] 
**description** | **str** | Chassis description | [optional] 
**service_tag** | **str** | Service tag of the chassis | [optional] 
**firmware_version** | **str** | Firmware version of the chassis | [optional] 
**psnt** | **str** | PSNT of the chassis | [optional] 
**moid** | **str** | MOID of the chassis | [optional] 
**model** | **str** | Model of the chassis | [optional] 
**render_category** | **str** | Dell render category of the chassis | [optional] 
**generation** | **int** | VxRail generation of the chassis | [optional] 
**health** | **str** | Health status of the chassis | [optional] 
**missing** | **bool** | Whether the chassis health status is critical. Supported values are false (not critical) and true (critical) | [optional] 
**hosts** | [**list[HostBasicInfoV5]**](HostBasicInfoV5.md) |  | [optional] 
**witness** | [**list[WitnessBasicInfoV1]**](WitnessBasicInfoV1.md) | Witness information of the chassis. | [optional] 
**power_supplies** | [**list[PowerSupplyInfo]**](PowerSupplyInfo.md) |  | [optional] 
**chassis_manager_fw_version** | **str** | Firmware version of the chassis manager. | [optional] 
**bay** | **bool** | Whether the chassis has a bay or not | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

