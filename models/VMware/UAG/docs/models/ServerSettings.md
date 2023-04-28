# openapi_client.model.server_settings.ServerSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**url** | str,  | str,  |  | [optional] 
**urlThumbprints** | str,  | str,  | List of acceptable SSL server certificate thumbprints for the proxyDestinationUrl. If blank, a valid certificate is required. If &#x27;*&#x27;, any certificate is allowed. Otherwise, this is a comma-separated list of thumbprints. A thumbprint is of the format [alg&#x3D;]xx:xx... where alg can be sha1(default) or md5 and the &#x27;xx&#x27; are hexidecimal digits. The &#x27;:&#x27; separator can also be a space or missing. Case in a thumbprint is ignored. | [optional] 
**[trustedCertificates](#trustedCertificates)** | list, tuple,  | tuple,  |  | [optional] 
**urlResponseRefreshInterval** | decimal.Decimal, int,  | decimal.Decimal,  |  | [optional] value must be a 64 bit integer
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

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

