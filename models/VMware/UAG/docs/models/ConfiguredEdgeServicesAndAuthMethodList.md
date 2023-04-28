# openapi_client.model.configured_edge_services_and_auth_method_list.ConfiguredEdgeServicesAndAuthMethodList

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**[edgeServiceList](#edgeServiceList)** | list, tuple,  | tuple,  | List of edge service with enabled status flag. | 
**tlsPortSharingEnabled** | bool,  | BoolClass,  | TLS port sharing enabled property. | 
**fipsEnabled** | bool,  | BoolClass,  | fips flag. | 
**[wrpAuthConsumeTypes](#wrpAuthConsumeTypes)** | list, tuple,  | tuple,  | List of wrp auth consume types. | 
**uagName** | str,  | str,  | Appliance Name | 
**[authMethodList](#authMethodList)** | list, tuple,  | tuple,  | List of auth method with enabled status flag. | 
**adminCertRolledBack** | bool,  | BoolClass,  | A read-only property to indicate if uploaded certificate on Admin interface was successful or it was rolled back to a generated self-signed cert | [optional] 
**user** | [**AdminUser**](AdminUser.md) | [**AdminUser**](AdminUser.md) |  | [optional] 
**[privileges](#privileges)** | list, tuple,  | tuple,  | Privileges granted to logged in user | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# edgeServiceList

List of edge service with enabled status flag.

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of edge service with enabled status flag. | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**ConfiguredEdgeService**](ConfiguredEdgeService.md) | [**ConfiguredEdgeService**](ConfiguredEdgeService.md) | [**ConfiguredEdgeService**](ConfiguredEdgeService.md) |  | 

# authMethodList

List of auth method with enabled status flag.

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of auth method with enabled status flag. | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**ConfiguredAuthMethod**](ConfiguredAuthMethod.md) | [**ConfiguredAuthMethod**](ConfiguredAuthMethod.md) | [**ConfiguredAuthMethod**](ConfiguredAuthMethod.md) |  | 

# wrpAuthConsumeTypes

List of wrp auth consume types.

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of wrp auth consume types. | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | must be one of ["SAML", "CERTIFICATE", ] 

# privileges

Privileges granted to logged in user

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | Privileges granted to logged in user | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | must be one of ["FULL", "CONFIG_RO", "LOGLEVEL_RW", "LOGS_DOWNLOAD", "CONFIG_DOWNLOAD", "PASSWORD_CHANGE", ] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

