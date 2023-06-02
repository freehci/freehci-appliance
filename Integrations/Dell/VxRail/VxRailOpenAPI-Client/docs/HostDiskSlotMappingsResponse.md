# HostDiskSlotMappingsResponse

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**host** | **str** | If host_serial_number is supplied in the request object, this property returns the host serial number. Otherwise, the property returns the host ID ip address. | 
**all_slots** | [**list[BayInfo]**](BayInfo.md) | Information about slot positions for all disk drives | [optional] 
**vsan_slots** | [**HostDiskSlotMappingsResponseVsanSlots**](HostDiskSlotMappingsResponseVsanSlots.md) |  | [optional] 
**non_vsan_slots** | [**list[BayInfo]**](BayInfo.md) | A list of all slot positions where a disk drive is claimed for non-vSAN usage | [optional] 
**diskgroup_type** | **str** |  | [optional] 
**unmanaged_slots** | [**list[BayInfo]**](BayInfo.md) | A list of all slot positions where a disk drive is claimed for unmanaged usage | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

