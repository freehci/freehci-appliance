# openapi_client.model.outbound_proxy_settings.OutboundProxySettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**proxyUrl** | str,  | str,  | Proxy Server Url | 
**name** | str,  | str,  | Name of the Proxy, should be unique. Allowed characters include letters and numbers of most languages and the special characters dot, hyphen, underscore and whitespace. | 
**[includedHosts](#includedHosts)** | list, tuple,  | tuple,  | List of all included Hosts through this proxy. atleast one host is required | 
**proxyType** | str,  | str,  | Type of Proxy  | [optional] must be one of ["HTTP", ] 
**[trustedCertificates](#trustedCertificates)** | list, tuple,  | tuple,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# includedHosts

List of all included Hosts through this proxy. atleast one host is required

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of all included Hosts through this proxy. atleast one host is required | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | 

# trustedCertificates

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  |  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

