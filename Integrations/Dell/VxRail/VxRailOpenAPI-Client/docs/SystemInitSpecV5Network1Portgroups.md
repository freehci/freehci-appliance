# SystemInitSpecV5Network1Portgroups

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the port group. This property is only for a ADVANCED_CUSTOMER_SUPPLIED_VDS nic_profile. | [optional] 
**type** | **str** | The type of portgroup. The VXRAILDISCOVERY option is only used for ADVANCED_VXRAIL_SUPPLIED_VDS or ADVANCED_CUSTOMER_SUPPLIED_VDS nic_profile. | [optional] 
**vlan_id** | **int** | The VLAN ID of the port group. If you use an ADVANCED_VXRAIL_SUPPLIED_VDS or ADVANCED_CUSTOMER_SUPPLIED_VDS nic_profile and sfs_disabled &#x3D; false , the VLAN ID for a VXRAILDISCOVERY portgroup type must be set to 3939. | [optional] 
**vmk_mtu** | **int** | The MTU value of vmkernel on selected traffic type. This value must be in range [1500, 9000]. This property is only supported for portgroup type [MANAGEMENT, DISCOVERY, VSAN, VMOTION, WITNESS] | [optional] 
**uplinks** | **list[str]** | A list of uplinks. This property is only used when nic_profile is ADVANCED_CUSTOMER_SUPPLIED_VDS and sfs_disabled is false | [optional] 
**lags** | **list[str]** | A list of link aggregation groups (LAG). This property is only used when nic_profile is ADVANCED_CUSTOMER_SUPPLIED_VDS and LAG is used on the portgroup. | [optional] 
**failover_order** | [**SystemInitSpecV5Network1FailoverOrder**](SystemInitSpecV5Network1FailoverOrder.md) |  | [optional] 
**load_balance_policy** | **str** | The load balance policy for portgroup | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

