# ChassisInfoV4

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the chassis | [optional] 
**sn** | **str** | Serial number of the chassis | [optional] 
**part_number** | **str** | Part number of the chassis | [optional] 
**description** | **str** | Chassis description | [optional] 
**service_tag** | **str** | Service tag of the chassis | [optional] 
**psnt** | **str** | PSNT of the chassis | [optional] 
**model** | **str** | Model of the chassis | [optional] 
**render_category** | **str** | Dell render category of the chassis | [optional] 
**generation** | **int** | VxRail generation of the chassis | [optional] 
**health** | **str** | Health status of the chassis | [optional] 
**missing** | **bool** | Whether the chassis health status is critical. Supported values are false (not critical) and true (critical) | [optional] 
**hosts** | [**list[HostBasicInfoV4]**](HostBasicInfoV4.md) |  | [optional] 
**power_supplies** | [**list[PowerSupplyInfo]**](PowerSupplyInfo.md) |  | [optional] 
**bay** | **bool** | Whether the chassis has a bay or not | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

