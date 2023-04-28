# openapi_client.model.snmp_settings.SnmpSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**version** | str,  | str,  | SNMP version | [optional] must be one of ["V1_V2C", "V3", ] 
**usmUser** | str,  | str,  | SNMPv3 User-based Security Model (USM) User name | [optional] 
**engineID** | str,  | str,  | An SNMP engine&#x27;s administratively-unique identifier used for SNMP v3 | [optional] 
**securityLevel** | str,  | str,  | SNMPv3 Security Level | [optional] must be one of ["NO_AUTH_NO_PRIV", "AUTH_NO_PRIV", "AUTH_PRIV", ] 
**authPassword** | str,  | str,  | SNMPv3 Authentication Password | [optional] 
**privacyAlgorithm** | str,  | str,  | SNMPv3 Privacy Algorithm | [optional] must be one of ["AES", "DES", ] 
**privacyPassword** | str,  | str,  | SNMPv3 Privacy Password | [optional] 
**authAlgorithm** | str,  | str,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

