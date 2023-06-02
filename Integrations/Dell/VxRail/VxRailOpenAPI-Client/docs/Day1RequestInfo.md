# Day1RequestInfo

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The returned request_id from a running cluster configuration (POST /v1/system/initialize) | 
**state** | **str** | The current state of execution | [optional] 
**step** | **str** | The current step being run | [optional] 
**owner** | **str** | The owner of the request | [optional] 
**progress** | **int** | The progress of the current execution (as a percentage) | 
**start_time** | **int** | The start time of the current execution | [optional] 
**end_time** | **int** | The end time of the current execution | [optional] 
**extension** | [**Day1RequestInfoExtension**](Day1RequestInfoExtension.md) |  | [optional] 
**detail** | **str** | Reserved field | [optional] 
**error** | **str** | Reserved field | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

