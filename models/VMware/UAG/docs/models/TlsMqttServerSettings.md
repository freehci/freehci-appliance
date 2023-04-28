# openapi_client.model.tls_mqtt_server_settings.TlsMqttServerSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**mqttClientCertCertPem** | str,  | str,  | Client certificate in PEM format. To be used during TLS communicationwith mqtt server. Only provide if mqtt server needs mutual (client-cert) authentication | [optional] 
**mqttClientCertKeyPem** | str,  | str,  | Client certificate Private key in PEM format.Only provide if mqtt server needs mutual (client-cert) authentication | [optional] 
**mqttServerCACertPem** | str,  | str,  | CA certificate of the mqtt server in PEM format. | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

