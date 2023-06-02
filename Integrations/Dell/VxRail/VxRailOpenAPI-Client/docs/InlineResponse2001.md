# InlineResponse2001

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Description of the VxRail system. | 
**version** | **str** | Software version of the VxRail appliance. | 
**installed_time** | **int** | Installation time of the VxRail appliance software. | [optional] 
**health** | **str** | Health status of the VxRail system. | 
**network_connected** | **bool** | Connection status of the host with the internet. | 
**vc_connected** | **bool** | vCenter connection status. | 
**upgrade_status** | **str** | The upgrade status of the VxRail appliance software. | [optional] 
**installed_components** | [**list[InstalledComponent]**](InstalledComponent.md) | Software components installed in the VxRail system. | [optional] 
**deployment_type** | **list[str]** | Information about the type of cluster deployed. | 
**cluster_host_count** | **int** | Number of hosts in the cluster. | 
**satellite_host_count** | **object** | Number of VxRail managed satellite nodes. | 
**is_external_vc** | **bool** | Whether the vCenter is external. | 
**logical_view_status** | **bool** | Enabled status of the VxRail manager logical view. | 
**shared_storage** | [**list[SharedStorage]**](SharedStorage.md) | Information about shared storage in the VxRail cluster. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

