# UpgradeSpecV3

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bundle_file_locator** | **str** | The full path of the single upgrade bundle or first package of a multiple part upgrade bundle. [Note] Multi-part upgrades must follow required naming conventions -- (1) The first file (the installer file) contains \&quot;installer\&quot; in the name. (2) Users must not rename any files belonging to the multi-part bundle. | 
**vxrail** | [**VxRailManagerSpec**](VxRailManagerSpec.md) |  | 
**vcenter** | [**VcenterEmbeddedPSCSpec**](VcenterEmbeddedPSCSpec.md) |  | 
**witness** | [**WitnessSpec**](WitnessSpec.md) |  | [optional] 
**upgrade_sequence** | [**UpgradeSequence**](UpgradeSequence.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

