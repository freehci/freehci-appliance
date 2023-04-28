# openapi_client.model.auth_method_settings.AuthMethodSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**name** | str,  | str,  | The name of the authentication method. | 
**className** | str,  | str,  | The name of the class that implements the authentication method. | [optional] 
**displayName** | str,  | str,  | The name of the method useful for display to the user. | [optional] 
**jarFile** | str,  | str,  | The path name of the JAR file that contains the authentication method. | [optional] 
**authMethod** | str,  | str,  | The formal name (URN) of the authentication method. | [optional] 
**versionNum** | str,  | str,  | The version of the authentication method. | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

