# openapi_client.model.modified_admin_user.ModifiedAdminUser

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**name** | str,  | str,  |  | [optional] 
**password** | str,  | str,  |  | [optional] 
**userId** | str,  | str,  |  | [optional] 
**enabled** | bool,  | BoolClass,  |  | [optional] 
**[roles](#roles)** | list, tuple,  | tuple,  |  | [optional] 
**adminPasswordSetTime** | str,  | str,  |  | [optional] 
**noOfDaysRemainingForPwdExpiry** | decimal.Decimal, int,  | decimal.Decimal,  |  | [optional] value must be a 32 bit integer
**userType** | str,  | str,  |  | [optional] must be one of ["INTERNAL", "EXTERNAL", ] 
**adminMonitoringPasswordPreExpired** | bool,  | BoolClass,  |  | [optional] 
**modifiedBy** | str,  | str,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# roles

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  |  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | must be one of ["ROLE_ADMIN", "ROLE_MONITORING", ] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

