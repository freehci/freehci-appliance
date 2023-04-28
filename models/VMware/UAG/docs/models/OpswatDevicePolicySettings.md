# openapi_client.model.opswat_device_policy_settings.OpswatDevicePolicySettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, bool, None, list, tuple, bytes, io.FileIO, io.BufferedReader,  | frozendict.frozendict, str, decimal.Decimal, BoolClass, NoneClass, tuple, bytes, FileIO |  | 

### Composed Schemas (allOf/anyOf/oneOf/not)
#### allOf
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[DevicePolicySettings](DevicePolicySettings.md) | [**DevicePolicySettings**](DevicePolicySettings.md) | [**DevicePolicySettings**](DevicePolicySettings.md) |  | 
[all_of_1](#all_of_1) | dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

# all_of_1

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**password** | str,  | str,  | Password for configured user on tenant. | 
**userName** | str,  | str,  | User name for configured tenant. | 
**[allowedStatuses](#allowedStatuses)** | list, tuple,  | tuple,  | List of statuses allowed by admin to gain access | [optional] 
**hostName** | str,  | str,  | Opswat host name. | [optional] 
**complianceCheckFastInterval** | decimal.Decimal, int,  | decimal.Decimal,  | Compliance check fast interval. | [optional] value must be a 64 bit integer
**complianceCheckInitialDelay** | decimal.Decimal, int,  | decimal.Decimal,  | Compliance Check initial delay | [optional] value must be a 64 bit integer
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# allowedStatuses

List of statuses allowed by admin to gain access

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of statuses allowed by admin to gain access | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | must be one of ["COMPLIANT", "NON_COMPLIANT", "OUT_OF_LICENSE_USAGE", "NOT_FOUND", "ASSESSMENT_PENDING", "OTHERS", ] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

