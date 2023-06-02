# HostFolderLCMControlSpec

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**failure_rate** | **int** | The failure rate of LCM batch job. failure_rate &#x3D; failed nodes count / total nodes count. This parameter is only valid for UPGRADE requests. Example: value 20 means the failure rate is 20%. | [optional] [default to 20]
**concurrent_size** | **int** | Number of nodes that can be upgraded in parallel. This parameter is only valid for UPGRADE requests. | [optional] [default to 20]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

