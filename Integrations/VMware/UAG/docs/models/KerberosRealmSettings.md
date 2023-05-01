# openapi_client.model.kerberos_realm_settings.KerberosRealmSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**[kdcHostNameList](#kdcHostNameList)** | list, tuple,  | tuple,  | kdc host name list | 
**name** | str,  | str,  | Name of the realm for Kerberos Constrained Delegation. | 
**kdcTimeout** | decimal.Decimal, int,  | decimal.Decimal,  | time to wait for kdc to respond. This value is provided in seconds.by default the value is set as 3 seconds (KDC default if not provided) | [optional] value must be a 32 bit integer
**noOfWRPsUsingThisRealm** | decimal.Decimal, int,  | decimal.Decimal,  | A read only property to indicate the number of web reverse proxies using this realm | [optional] value must be a 32 bit integer
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# kdcHostNameList

kdc host name list

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | kdc host name list | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

