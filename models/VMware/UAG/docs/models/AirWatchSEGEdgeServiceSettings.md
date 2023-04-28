# openapi_client.model.air_watch_seg_edge_service_settings.AirWatchSEGEdgeServiceSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, bool, None, list, tuple, bytes, io.FileIO, io.BufferedReader,  | frozendict.frozendict, str, decimal.Decimal, BoolClass, NoneClass, tuple, bytes, FileIO |  | 

### Composed Schemas (allOf/anyOf/oneOf/not)
#### allOf
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[EdgeServiceSettings](EdgeServiceSettings.md) | [**EdgeServiceSettings**](EdgeServiceSettings.md) | [**EdgeServiceSettings**](EdgeServiceSettings.md) |  | 
[all_of_1](#all_of_1) | dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

# all_of_1

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**airwatchComponentsInstalled** | str,  | str,  | AirWatch Components installed on this appliance | 
**apiServerUsername** | str,  | str,  | AirWatch Admin Console username | 
**organizationGroupCode** | str,  | str,  | Organization Group Code | 
**apiServerUrl** | str,  | str,  | AirWatch API Server URL Format is [http[s]://]hostname[:port]. | 
**apiServerPassword** | str,  | str,  | AirWatch Admin Console password | 
**airwatchServerHostname** | str,  | str,  | AirWatch Application Hostname | 
**reinitializeGatewayProcess** | bool,  | BoolClass,  | Forcibly re-initialize the Gateway | [optional] 
**outboundProxyHost** | str,  | str,  | Outbound Proxy Host | [optional] 
**outboundProxyPort** | str,  | str,  | Outbound Proxy Port | [optional] 
**outboundProxyUsername** | str,  | str,  | Outbound Proxy Username | [optional] 
**ntlmAuthentication** | bool,  | BoolClass,  | Whether the outbound proxy requires NTLM authentication? | [optional] 
**outboundProxyPassword** | str,  | str,  | Outbound Proxy Password | [optional] 
**airwatchOutboundProxy** | bool,  | BoolClass,  | Whether AirWatch Outbound Proxy used for AirWatch component(s)? | [optional] 
**airwatchAgentStartUpMode** | str,  | str,  |  | [optional] 
**serviceHost** | str,  | str,  | Service Hostname | [optional] 
**servicePort** | str,  | str,  | Service Port | [optional] 
**serviceStatsPort** | str,  | str,  | Service Stats Port | [optional] 
**serviceName** | str,  | str,  | Service Name | [optional] 
**serviceInstallStatus** | bool,  | BoolClass,  | Service Installation Status | [optional] 
**serviceInstallationMessage** | str,  | str,  | Service Installation Message | [optional] 
**runningMode** | str,  | str,  | AirWatch Edge Service Running Mode | [optional] 
**serviceConfigurationFailed** | bool,  | BoolClass,  | AirWatch Edge Service Configure Status | [optional] 
**memConfigurationId** | str,  | str,  | AirWatch MEM Configuration ID | [optional] 
**pfxCerts** | str,  | str,  |  | [optional] 
**pfxCertsPassword** | str,  | str,  |  | [optional] 
**pfxCertAlias** | str,  | str,  |  | [optional] 
**pfxCertsThumbprint** | str,  | str,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

