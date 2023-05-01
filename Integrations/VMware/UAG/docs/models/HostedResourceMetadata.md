# openapi_client.model.hosted_resource_metadata.HostedResourceMetadata

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**name** | str,  | str,  |  | [optional] 
**path** | str,  | str,  |  | [optional] 
**sha256Sum** | str,  | str,  |  | [optional] 
**params** | str,  | str,  |  | [optional] 
**flags** | [**Flags**](Flags.md) | [**Flags**](Flags.md) |  | [optional] 
**executable** | str,  | str,  |  | [optional] 
**isObtainedfromURL** | bool,  | BoolClass,  |  | [optional] 
**fileType** | str,  | str,  |  | [optional] must be one of ["Windows", "Mac", ] 
**[trustedSigningCertificates](#trustedSigningCertificates)** | list, tuple,  | tuple,  |  | [optional] 
**osType** | str,  | str,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# trustedSigningCertificates

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  |  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

