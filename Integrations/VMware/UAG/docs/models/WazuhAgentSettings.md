# openapi_client.model.wazuh_agent_settings.WazuhAgentSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, bool, None, list, tuple, bytes, io.FileIO, io.BufferedReader,  | frozendict.frozendict, str, decimal.Decimal, BoolClass, NoneClass, tuple, bytes, FileIO |  | 

### Composed Schemas (allOf/anyOf/oneOf/not)
#### allOf
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[SecurityAgentSettings](SecurityAgentSettings.md) | [**SecurityAgentSettings**](SecurityAgentSettings.md) | [**SecurityAgentSettings**](SecurityAgentSettings.md) |  | 
[all_of_1](#all_of_1) | dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

# all_of_1

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**wazuhServerHostAndPort** | str,  | str,  | The manager IP address or hostname and port separated by colon | 
**wazuhProtocol** | str,  | str,  | The communication protocol between the manager and the agent. | [optional] must be one of ["TCP", "UDP", ] 
**wazuhRegistrationHostAndPort** | str,  | str,  | Wazuh manager that is used for agent registration. | [optional] 
**wazuhRegistrationPassword** | str,  | str,  | Wazuh Registration Password. | [optional] 
**wazuhEnrollmentDelay** | decimal.Decimal, int,  | decimal.Decimal,  | The time that agentd should wait after a successful registration. | [optional] value must be a 64 bit integer
**wazuhKeepAliveInterval** | decimal.Decimal, int,  | decimal.Decimal,  | The time between agent checks for manager connection | [optional] value must be a 64 bit integer
**wazuhTimeReconnect** | decimal.Decimal, int,  | decimal.Decimal,  | The time interval for the agent to reconnect with the Wazuh manager when connectivity is lost. | [optional] value must be a 64 bit integer
**wazuhAgentName** | str,  | str,  | Wazuh Agent name. | [optional] 
**wazuhAgentGroups** | str,  | str,  | Wazuh Agent Groups. | [optional] 
**wazuhServerCACertificate** | str,  | str,  |  Certificate of Authority for Host SSL Validation. | [optional] 
**wazuhAgentCertificate** | str,  | str,  | CA signed certificate for SSL agent verification. | [optional] 
**wazuhAgentKey** | str,  | str,  | Key for SSL agent verification. | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

