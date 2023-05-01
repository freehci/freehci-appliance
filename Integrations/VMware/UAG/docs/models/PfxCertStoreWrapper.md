# openapi_client.model.pfx_cert_store_wrapper.PfxCertStoreWrapper

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**pfxKeystore** | str,  | str,  | PFX certificate store in base64 encoded format | 
**password** | str,  | str,  | PFX certificate store password | [optional] 
**alias** | str,  | str,  | If the pfx certificate store has multiple certificates then an alias has to be provided. This is optional by default for pfx certificate store having only one certificate | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

