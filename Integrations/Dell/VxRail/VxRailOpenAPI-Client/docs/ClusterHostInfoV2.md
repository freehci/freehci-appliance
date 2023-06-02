# ClusterHostInfoV2

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID number of the host. | [optional] 
**serial_number** | **str** | Serial number of the host. | [optional] 
**slot** | **int** | Rack slot position where the VxRail host appliance is installed. | [optional] 
**host_name** | **str** | Indicates the hostname. | [optional] 
**appliance_id** | **str** | Host appliance ID. | [optional] 
**model** | **str** | Host model. | [optional] 
**is_primary_node** | **bool** | Whether the node is a primary node. | [optional] 
**cluster_affinity** | **bool** | Whether the node is installed in current cluster. | [optional] 
**discovered_date** | **int** | Discovered date. | [optional] 
**bios_uuid** | **str** | BIOS UUID. | [optional] 
**segment_label** | **str** | Segment label. | [optional] 
**manufacturer** | **str** | Manufacturer of the host. | [optional] 
**psnt** | **str** | Product serial number tag (PSNT) of the host. | [optional] 
**led_status** | **str** | State of the chassis LED indicator for the host. | [optional] 
**health** | **str** | Health status of the VxRail system. Supported values are Critical, Error, Warning, and Healthy. | [optional] 
**missing** | **bool** | Whether the chassis health status is critical. Supported values are false (not critical) and true (critical). | [optional] 
**ip_set** | [**ClusterHostInfoIpSet**](ClusterHostInfoIpSet.md) |  | [optional] 
**ip_set_ipv6** | [**ClusterHostInfoV2IpSetIpv6**](ClusterHostInfoV2IpSetIpv6.md) |  | [optional] 
**tpm_present** | **bool** | Whether a TPM security device is installed on the VxRail host. | [optional] 
**operational_status** | **str** | Operational status of the host. | [optional] 
**power_status** | **str** | Power supply status of the host. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

