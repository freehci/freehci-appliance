# openapi_client.model.radius_auth_method_settings.RadiusAuthMethodSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**numAttempts** | str,  | str,  | Number of attempts to Radius server | 
**hostName** | str,  | str,  | Radius server hostname/address | 
**realmSuffix** | str,  | str,  | Realm suffix | 
**enableBasicMSCHAPv2Validation_1** | bool,  | BoolClass,  | Enable basic MSCHAPv2 validation | 
**enableBasicMSCHAPv2Validation_2** | bool,  | BoolClass,  | Enable basic MSCHAPv2 validation for secondary server | 
**enabled** | bool,  | BoolClass,  | Enable Radius Adapter | 
**serverTimeout** | str,  | str,  | Server timeout in seconds | 
**showDomainIfUserInputAvailable** | bool,  | BoolClass,  | Display Domain on Login Page | 
**accountingPort_2** | str,  | str,  | Accounting port for secondary server | 
**numIterations** | str,  | str,  | Number of authentication attempts allowed | 
**radiusCustomPassphraseHint** | str,  | str,  | Custom passphrase hint for login page | 
**authPort** | str,  | str,  | Authentication port | 
**numAttempts_2** | str,  | str,  | Number of attempts to secondary Radius server | 
**authType** | str,  | str,  | Authentication type | must be one of ["PAP", "CHAP", "MSCHAP1", "MSCHAP2", ] 
**enabledAux** | bool,  | BoolClass,  | Enable secondary server | 
**sharedSecret** | str,  | str,  | Shared secret | 
**sharedSecret_2** | str,  | str,  | Shared secret for secondary server | 
**[nameIdSuffix](#nameIdSuffix)** | dict, frozendict.frozendict,  | frozendict.frozendict,  | Name Id Suffix | 
**directAuthChainedUsername** | bool,  | BoolClass,  | Enable direct authentication to Radius server during auth chaining | 
**hostName_2** | str,  | str,  | Radius server hostname/address for secondary server | 
**authType_2** | str,  | str,  | Authentication type for secondary server | must be one of ["PAP", "CHAP", "MSCHAP1", "MSCHAP2", ] 
**radiusDisplayHint** | str,  | str,  | Login page passphrase hint | 
**serverTimeout_2** | str,  | str,  | Server timeout in seconds for secondary server | 
**accountingPort** | str,  | str,  | Accounting port | 
**realmPrefix_2** | str,  | str,  | Realm prefix for secondary server | 
**name** | str,  | str,  | The name of the authentication method. | 
**authPort_2** | str,  | str,  | Authentication port for secondary server | 
**realmPrefix** | str,  | str,  | Realm prefix | 
**realmSuffix_2** | str,  | str,  | Realm suffix for secondary server | 
**className** | str,  | str,  | The name of the class that implements the authentication method. | [optional] 
**displayName** | str,  | str,  | The name of the method useful for display to the user. | [optional] 
**jarFile** | str,  | str,  | The path name of the JAR file that contains the authentication method. | [optional] 
**authMethod** | str,  | str,  | The formal name (URN) of the authentication method. | [optional] 
**versionNum** | str,  | str,  | The version of the authentication method. | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# nameIdSuffix

Name Id Suffix

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  | Name Id Suffix | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

