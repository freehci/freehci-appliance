# openapi_client.model.ws_portal_edge_service_settings.WsPortalEdgeServiceSettings

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
**instanceId** | str,  | str,  | Instance ID for identifying a Web reverse proxy instance | 
**proxyPattern** | str,  | str,  | Proxy pattern | 
**externalUrl** | str,  | str,  | Override the default External URL value. Format is [https://]host[:port]. Default value (Access Point&#x27;s host:443) will be used if not set. | [optional] 
**unSecurePattern** | str,  | str,  | Unsecure URL pattern for login page, static content | [optional] 
**authCookie** | str,  | str,  | Authentication Cookie name | [optional] 
**loginRedirectURL** | str,  | str,  | login Redirect URL | [optional] 
**proxyHostPattern** | str,  | str,  | Proxy host pattern | [optional] 
**keyTabPrincipalName** | str,  | str,  | KeyTab principal name to identify the keyTab to usefor Kerberos Constrained Delegation | [optional] 
**targetSPN** | str,  | str,  | Target Service principal name. If not provided and keytab principal is set then it will be worked as HTTP/&lt;host name of web rev proxy&gt;@&lt;realm of the principal name chosen&gt; | [optional] 
**keyTabFilePath** | str,  | str,  |  | [optional] 
**idpEntityID** | str,  | str,  | Configure IDP entity for identity bridging | [optional] 
**allowedAudiences** | str,  | str,  | Comma separated values of allowed audiences to be matched againstaudience restriction in the SAML assertion. If empty or not setup then audience restrictions will notbe validated while validating SAML assertion | [optional] 
**landingPagePath** | str,  | str,  | Configure the path to landing page in IDP initiated flow. By defaultpath will be set to &#x27;/&#x27; | [optional] 
**userNameHeader** | str,  | str,  | Configure the name of the USER ID header to authenticate the userfor USER name based auth | [optional] 
**wrpAuthConsumeType** | str,  | str,  |  | [optional] must be one of ["SAML", "CERTIFICATE", ] 
**keyTabRealm** | str,  | str,  |  | [optional] 
**[samlAttributeHeaderMap](#samlAttributeHeaderMap)** | dict, frozendict.frozendict,  | frozendict.frozendict,  |  | [optional] 
**[securityHeaders](#securityHeaders)** | dict, frozendict.frozendict,  | frozendict.frozendict,  | Key,Value pair of the security headers to be added to response | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# samlAttributeHeaderMap

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**any_string_name** | str,  | str,  | any string name can be used but the value must be the correct type | [optional] 

# securityHeaders

Key,Value pair of the security headers to be added to response

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  | Key,Value pair of the security headers to be added to response | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**any_string_name** | str,  | str,  | any string name can be used but the value must be the correct type | [optional] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

