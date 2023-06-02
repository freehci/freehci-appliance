# DiscoveredNodeInfoV2

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**DiscoveredNodeIdInfo**](DiscoveredNodeIdInfo.md) |  | 
**esxi_version** | **str** | The ESXi version of the node | 
**vxm_system_version** | **str** | The VxRail system version | [optional] 
**evo_uuid** | **str** | UUID of VxRail Manager VM | [optional] 
**primary_ip** | **str** | The IPv6 address of the first virtual NIC (vmk0) of the node (with a \&quot;:%eth1\&quot; suffix) | [optional] 
**fallback_ip** | **str** | Null. (For internal use only) | [optional] 
**idrac_ip** | **str** | The iDRAC IP address of the node | 
**prerecoded_ip** | **str** | Null. (For internal use only) | [optional] 
**ip** | **str** | The IPv4 address of the node | [optional] 
**asset_tag** | **str** | The asset tag of the node | 
**serial_number** | **str** | The serial number of the node | 
**primary** | **bool** | Whether the node is the primary node | 
**cluster_affinity** | **str** | Null. (For internal use only) | [optional] 
**ssl_thumbprint** | **str** | SSL thumbprint of the node | 
**ssh_thumbprint** | **str** | SSH thumbprint of the node | 
**uuid** | [**DiscoveredNodeUuidInfo**](DiscoveredNodeUuidInfo.md) |  | [optional] 
**hardware_profile** | [**DiscoveredNodeHardwareProfileInfo**](DiscoveredNodeHardwareProfileInfo.md) |  | 
**discovered_date** | **int** | Discovered date of the node | [optional] 
**configuration_state** | **str** | Configuration state of the node | [optional] 
**model** | **str** | Platform model of the node | 
**ip_set** | **object** | Null. (For internal use only) | [optional] 
**node_version_info** | [**DiscoveredNodeVersionInfo**](DiscoveredNodeVersionInfo.md) |  | [optional] 
**violations** | **list[str]** | Messages about hardware profile violations | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

