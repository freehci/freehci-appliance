# openapi_client.model.device_policy_settings.DevicePolicySettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**name** | str,  | str,  | Name of the device policy check service provider. | 
**[hostedResourceMap](#hostedResourceMap)** | dict, frozendict.frozendict,  | frozendict.frozendict,  |  | [optional] 
**settingsId** | str,  | str,  |  | [optional] 
**complianceCheckInterval** | decimal.Decimal, int,  | decimal.Decimal,  | Compliance check interval. | [optional] value must be a 64 bit integer
**complianceCheckTimeunit** | str,  | str,  | Timeunit for compliance check Interval | [optional] must be one of ["NANOSECONDS", "MICROSECONDS", "MILLISECONDS", "SECONDS", "MINUTES", "HOURS", "DAYS", ] 
**complianceServerHealthCheckInterval** | decimal.Decimal, int,  | decimal.Decimal,  | Account details check interval from compliance server | [optional] value must be a 32 bit integer
**[allowedStatuses](#allowedStatuses)** | list, tuple,  | tuple,  | List of statuses allowed by admin to gain access | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# hostedResourceMap

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**any_string_name** | [**ResourceSettings**](ResourceSettings.md) | [**ResourceSettings**](ResourceSettings.md) | any string name can be used but the value must be the correct type | [optional] 

# allowedStatuses

List of statuses allowed by admin to gain access

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of statuses allowed by admin to gain access | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**DeviceStatus**](DeviceStatus.md) | [**DeviceStatus**](DeviceStatus.md) | [**DeviceStatus**](DeviceStatus.md) |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

