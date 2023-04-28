# openapi_client.model.tls_syslog_server_settings.TlsSyslogServerSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**hostname** | str,  | str,  |  | [optional] 
**port** | decimal.Decimal, int,  | decimal.Decimal,  |  | [optional] value must be a 32 bit integer
**acceptedPeer** | str,  | str,  |  | [optional] 
**syslogServerCACertPemV2** | str,  | str,  | CA certificate of the syslog server in PEM format. Mandatory field if syslog type is TLS | [optional] 
**syslogClientCertPemV2** | str,  | str,  | Client certificate in PEM format. To be used during TLS communicationwith syslog server. Only provide if syslog server needs mutual (client-cert) authentication | [optional] 
**syslogClientCertKeyPemV2** | str,  | str,  | Client certificate Private key in PEM format. Only provide if syslog server needs mutual (client-cert) authentication | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

