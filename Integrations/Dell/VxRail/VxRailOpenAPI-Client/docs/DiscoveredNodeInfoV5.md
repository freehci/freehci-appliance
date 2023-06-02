# DiscoveredNodeInfoV5

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**DiscoveredNodeIdInfo**](DiscoveredNodeIdInfo.md) |  | 
**esxi_version** | **str** | ESXi version of the node | 
**vxm_system_version** | **str** | VxRail system version | [optional] 
**evo_uuid** | **str** | UUID of the VxRail Manager VM | [optional] 
**primary_ip** | **str** | The IPv6 address of the first virtual NIC (vmk0) of the node | [optional] 
**idrac_ip** | **str** | iDRAC IPv4 address of the node | [optional] 
**idrac_ipv6** | **str** | Internal use only | [optional] 
**ip** | **str** | IPv4 address of the node | [optional] 
**ipv6** | **str** | Internal use only | [optional] 
**asset_tag** | **str** | Asset tag of the node | 
**serial_number** | **str** | Serial number of the node | 
**primary** | **bool** | Whether the node is the primary node | 
**ssl_thumbprint** | **str** | SSL thumbprint of the node | 
**ssh_thumbprint** | **str** | SSH thumbprint of the node | 
**uuid** | [**DiscoveredNodeUuidInfo**](DiscoveredNodeUuidInfo.md) |  | [optional] 
**hardware_profile** | [**DiscoveredNodeHardwareProfileInfo**](DiscoveredNodeHardwareProfileInfo.md) |  | 
**disk_group_config** | [**DiscoveredNodeDiskGroupConfigInfo**](DiscoveredNodeDiskGroupConfigInfo.md) |  | [optional] 
**storage_types** | **list[str]** | Storage type of the node | 
**configuration_state** | **str** | Configuration state of the node | [optional] 
**model** | **str** | Appliance model of the node | 
**violations** | **list[str]** | Messages about hardware profile violations | [optional] 
**vlcm_software_spec** | [**VlcmImageDepotInfo**](VlcmImageDepotInfo.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

