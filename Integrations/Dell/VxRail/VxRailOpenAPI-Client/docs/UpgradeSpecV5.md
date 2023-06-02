# UpgradeSpecV5

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bundle_file_locator** | **str** | The full path of the single upgrade bundle or first package of a multiple part upgrade bundle. Multiple part upgrades must follow the mentioned criteria -- (1) The first file (the installer file) contains \&quot;installer\&quot; in the name. (2) Do not rename any files belonging to the multiple part bundle. | 
**vxrail** | [**VxRailManagerSpec**](VxRailManagerSpec.md) |  | 
**vcenter** | [**VcenterEmbeddedPSCSpecV4**](VcenterEmbeddedPSCSpecV4.md) |  | 
**witness** | [**WitnessSpec**](WitnessSpec.md) |  | [optional] 
**upgrade_sequence** | [**UpgradeSequence**](UpgradeSequence.md) |  | [optional] 
**target_hosts** | [**list[HostBaseSpec]**](HostBaseSpec.md) | (Optional) Hosts to be upgraded. The target_hosts object only applies to a cluster when vLCM is enabled. | [optional] 
**update_rules** | [**UpgradeSpecV5UpdateRules**](UpgradeSpecV5UpdateRules.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

