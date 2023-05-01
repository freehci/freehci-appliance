# openapi_client.model.syslog_server_settings.SyslogServerSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**syslogCategory** | str,  | str,  | Type of log to be sent to remote syslog server.  Valid values [ALL, AUDIT_ONLY] | [optional] 
**[syslogCategoryList](#syslogCategoryList)** | list, tuple,  | tuple,  | Types of log to be sent to remote syslog server.  Valid values [ALL, AUDIT, APPLICATION, TRACEABILITY, STATS, DEPLOYMENT]. If both syslogCategory and syslogCategoryList are configured, syslogCategory is ignored. | [optional] 
**syslogFormat** | str,  | str,  | Format of log to be sent to remote syslog server.  Valid values [TEXT, JSON_TITAN, JSON_EXPANDED] | [optional] must be one of ["TEXT", "JSON_TITAN", "JSON_EXPANDED", ] 
**sysLogType** | str,  | str,  | Type of communication to be used for syslog server. Valid values [UDP, TCP, TLS, MQTT] | [optional] must be one of ["UDP", "TCP", "TLS", "MQTT", ] 
**syslogSystemMessagesEnabledV2** | bool,  | BoolClass,  | Enable System Syslog Messages. | [optional] 
**syslogUrl** | str,  | str,  | syslog server Url for TCP/UDP | [optional] 
**mqttTopic** | str,  | str,  | mqtt server topic name | [optional] 
**syslogSettingName** | str,  | str,  | Unique identifier for each syslog settings | [optional] 
**tlsSyslogServerSettings** | [**TlsSyslogServerSettings**](TlsSyslogServerSettings.md) | [**TlsSyslogServerSettings**](TlsSyslogServerSettings.md) |  | [optional] 
**tlsMqttServerSettings** | [**TlsMqttServerSettings**](TlsMqttServerSettings.md) | [**TlsMqttServerSettings**](TlsMqttServerSettings.md) |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# syslogCategoryList

Types of log to be sent to remote syslog server.  Valid values [ALL, AUDIT, APPLICATION, TRACEABILITY, STATS, DEPLOYMENT]. If both syslogCategory and syslogCategoryList are configured, syslogCategory is ignored.

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | Types of log to be sent to remote syslog server.  Valid values [ALL, AUDIT, APPLICATION, TRACEABILITY, STATS, DEPLOYMENT]. If both syslogCategory and syslogCategoryList are configured, syslogCategory is ignored. | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | must be one of ["ALL", "AUDIT", "APPLICATION", "SYSTEM", "TRACEABILITY", "STATS", "DEPLOYMENT", ] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

