# SatelliteNodeExpansionNodeSpec

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**customer_supplied** | [**SatelliteNodeCustomerSuppliedSpec**](SatelliteNodeCustomerSuppliedSpec.md) |  | 
**hostname** | **str** | Hostname of the host | 
**domain_name** | **str** | Domain name of the host | 
**accounts** | [**NodeAccount**](NodeAccount.md) |  | 
**network** | [**list[SatelliteNodeNetwork]**](SatelliteNodeNetwork.md) | An array of network information for the host components | 
**dns_servers** | **list[str]** | An array of dns servers information for the host components | 
**ntp_servers** | **list[str]** | An array of ntp servers information for the host components | [optional] 
**syslog_servers** | **list[str]** | An array of syslog servers information for the host components | [optional] 
**geo_location** | [**GeoLocation**](GeoLocation.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

