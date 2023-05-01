# openapi_client.model.jwt_issuer_settings.JWTIssuerSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**name** | str,  | str,  |  | [optional] 
**issuer** | str,  | str,  |  | [optional] 
**jwtType** | str,  | str,  |  | [optional] must be one of ["CONSUMER", "PRODUCER", ] 
**jsonWebKeySet** | str,  | str,  |  | [optional] 
**jwtSigningPemCertSettings** | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) |  | [optional] 
**jwtSigningPfxCertSettings** | [**PfxCertStoreWrapper**](PfxCertStoreWrapper.md) | [**PfxCertStoreWrapper**](PfxCertStoreWrapper.md) |  | [optional] 
**[encryptionPublicKey](#encryptionPublicKey)** | list, tuple,  | tuple,  | JWT Issuer encryption public key Settings  | [optional] 
**encryptionPublicKeyURLSettings** | [**ServerSettings**](ServerSettings.md) | [**ServerSettings**](ServerSettings.md) |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# encryptionPublicKey

JWT Issuer encryption public key Settings 

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | JWT Issuer encryption public key Settings  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

