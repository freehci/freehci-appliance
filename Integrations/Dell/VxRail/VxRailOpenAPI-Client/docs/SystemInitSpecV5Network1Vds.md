# SystemInitSpecV5Network1Vds

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the defined vSphere Distributed Switch. This property is only for ADVANCED_CUSTOMER_SUPPLIED_VDS nic_profile. | [optional] 
**mtu** | **int** | The MTU value of the vSphere Distributed Switch. This value must be in the [1500, 9000] range. This property is only supported for the V-VDS or Multi-VDS portgroup types. This property is not supported for customer-supplied VDS or vSAN 2-node clusters. | [optional] 
**nic_mappings** | [**list[SystemInitSpecV5Network1NicMappings]**](SystemInitSpecV5Network1NicMappings.md) | This property is only used for a ADVANCED_VXRAIL_SUPPLIED_VDS and ADVANCED_CUSTOMER_SUPPLIED_VDS nic_profile | [optional] 
**portgroups** | [**list[SystemInitSpecV5Network1Portgroups]**](SystemInitSpecV5Network1Portgroups.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

