# openapi_client.model.core_dump_settings.CoreDumpSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**maxSizeMb** | decimal.Decimal, int,  | decimal.Decimal,  | Maximum size of the core dump to be collected in MB. [16-2048] | [optional] value must be a 32 bit integer
**maxTimeSeconds** | decimal.Decimal, int,  | decimal.Decimal,  | Maximum duration in seconds post which core dump collection is aborted. Use zero to disable core dump collection. [0-900] | [optional] value must be a 32 bit integer
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

