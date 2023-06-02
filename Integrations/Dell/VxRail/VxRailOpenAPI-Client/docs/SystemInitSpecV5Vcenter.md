# SystemInitSpecV5Vcenter

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**customer_supplied** | **bool** | Whether the vCenter server is customer supplied (external) or VxRail integrated (internal). Supported values are true for customer supplied and false for integrated. | [optional] 
**customer_supplied_vc_name** | **str** | The FQDN of the vCenter server. This property is only provided if the vCenter server is customer supplied. | [optional] 
**vxrail_supplied_vc_ip** | **str** | The IP address of the VxRail integrated vCenter server. This property is only provided if the vCenter server is VxRail integrated. | [optional] 
**vxrail_supplied_vc_ipv6** | **str** | Internal use only | [optional] 
**vxrail_supplied_vc_name** | **str** | The hostname of the VxRail integrated vCenter server. This property is only provided if the vCenter server is VxRail integrated. | [optional] 
**datacenter_name** | **str** | The name of the datacenter. This property is only provided if the vCenter server is customer supplied. | [optional] 
**cluster_name** | **str** | The name of the cluster. This property is only provided if the vCenter server is customer supplied. | [optional] 
**auto_accept_vc_cert** | **bool** | Whether to automatically download the vCenter root certificate. True means VxRail Manager will download the vCenter root certificate automatically. False means users should provide the vCenter root certificate manually. | [optional] 
**accounts** | [**SystemInitSpecV5VcenterAccounts**](SystemInitSpecV5VcenterAccounts.md) |  | [optional] 
**sso_domain** | [**SystemInitSpecV5VcenterSsoDomain**](SystemInitSpecV5VcenterSsoDomain.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

