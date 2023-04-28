# openapi_client.model.view_edge_service_settings.ViewEdgeServiceSettings

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
**pcoipEnabled** | bool,  | BoolClass,  | Enable / disable PC over IP support. | 
**tunnelEnabled** | bool,  | BoolClass,  | Enable / disable Secure Tunnel support. | 
**blastEnabled** | bool,  | BoolClass,  | Enable / disable BLAST secure gateway support. | 
**pcoipExternalUrl** | str,  | str,  | Override the default PCoIP External URL value. Format is [pcoip://]IP[:port]. Default value (Access Point&#x27;s IP address:4172) will be used if not set. | [optional] 
**blastExternalUrl** | str,  | str,  | Override the default BLAST External URL value. Format is [https://]host[:port][?queryParams]. Default value (Access Point&#x27;s host:443) will be used if not set. | [optional] 
**blastReverseConnectionEnabled** | bool,  | BoolClass,  | Enable / disable BLAST reverse connection. | [optional] 
**blastReverseExternalUrlOutside** | str,  | str,  | Override the internet facing BLAST Reverse External URL value. Format is [https://]host[:port]. More values can be provided in comma separated format. | [optional] 
**blastReverseExternalUrlInside** | str,  | str,  | Override the internal facing BLAST Reverse External URL value. Format is [https://]host[:port]. More values can be provided in comma separated format. | [optional] 
**proxyBlastPemCert** | str,  | str,  | Certificate of any proxy if present in front of UAG for forwarding blast connections. In PEM format and only leaf certificate | [optional] 
**blastAllowedHostHeaderValues** | str,  | str,  | Comma separated list of all allowed host[:port] combinations. If non empty, then incoming host header should match one of the host name in the list. Use &#x27;__empty__&#x27; to allow empty value. &#x27;__empty__&#x27; can also be used along with host[:port] combination in a comma-separated format. | [optional] 
**proxyBlastSHA1Thumbprint** | str,  | str,  | SHA1 thumbprint of any proxy certificate in front of UAG forforwarding blast connections | [optional] 
**proxyBlastSHA256Thumbprint** | str,  | str,  | SHA256 thumbprint of any proxy certificate in front of UAG for for forwarding blast connections. | [optional] 
**tunnelExternalUrl** | str,  | str,  | Override the default Secure Tunnel External URL value. Format is [https://]host[:port]. Default value (Access Point&#x27;s host:443) will be used if not set. | [optional] 
**proxyTunnelPemCert** | str,  | str,  | Certificate of any proxy if present in front of UAG for forwarding tunnel connections. In PEM format and only leaf certificate | [optional] 
**xmlAPISigningCertificateFlag** | str,  | str,  | XML Signing Certificate Type  | [optional] must be one of ["PEM", "PFX", "NONE", ] 
**xmlSigningPemCertSettings** | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) |  | [optional] 
**xmlSigningSwitch** | str,  | str,  | XML Signing Switch Settings  | [optional] must be one of ["ON", "OFF", "AUTO", ] 
**xmlSigningEnabled** | bool,  | BoolClass,  |  | [optional] 
**proxyTunnelSHA1Thumbprint** | str,  | str,  | SHA1 thumbprint of any proxy certificate in front of UAG forforwarding tunnel connections | [optional] 
**proxyTunnelSHA256Thumbprint** | str,  | str,  | SHA256 thumbprint of any proxy certificate in front of UAG for for forwarding tunnel connections. | [optional] 
**proxyPattern** | str,  | str,  | Regular expression matching URI paths that are forwarded to the destination URL. | [optional] 
**smartCardHintPrompt** | bool,  | BoolClass,  | Enable / disable the password hint for Certificate - Auth | [optional] 
**matchWindowsUserName** | bool,  | BoolClass,  | This boolean variable if configured true for securId-auth then then we enforce SecureID and Windows user name matching | [optional] 
**gatewayLocation** | str,  | str,  | This is gateway-location header value which is used for Fine Grained Policy(FGP) by the backend services | [optional] 
**windowsSSOEnabled** | bool,  | BoolClass,  | This boolean variable if configured true for radius-auth then then the Windows login should use the name and passcode that was used in the first successful RADIUS access-request | [optional] 
**logoutOnCertRemoval** | bool,  | BoolClass,  | This boolean variable if configured true for cert-auth then then UAG would use the configured value to communicate to client whether to logout when certificateis removed (smart card removed/device cert removed) | [optional] 
**udpTunnelServerEnabled** | bool,  | BoolClass,  | Enable UDP tunnel server | [optional] 
**queryBrokerInterval** | decimal.Decimal, int,  | decimal.Decimal,  | Querying connection broker polling time in seconds | [optional] value must be a 32 bit integer
**disableHtmlAccess** | bool,  | BoolClass,  | Disable resource lauch using Horizon Html client | [optional] 
**complianceCheckOnAuthentication** | bool,  | BoolClass,  | Enables Compliance Check On Authentication | [optional] 
**proxyDestinationIPSupport** | str,  | str,  | Configuration for backend proxy (ideally View CS) supporting IP modes | [optional] must be one of ["IPV4", "IPV6", "IPV4_IPV6", ] 
**clientEncryptionMode** | str,  | str,  | Client encryption mode | [optional] must be one of ["DISABLED", "ALLOWED", "REQUIRED", ] 
**radiusClassAttributeList** | str,  | str,  | Class attributes to be used to authorize the user in case of Radiusauthentication. This is a comma separated list. Only applicable if auth method is Radius | [optional] 
**foreverAppsEnabled** | bool,  | BoolClass,  | Enable Forever Applications | [optional] 
**pcoipDisableLegacyCertificate** | bool,  | BoolClass,  |  | [optional] 
**[securityHeaders](#securityHeaders)** | dict, frozendict.frozendict,  | frozendict.frozendict,  | Key,Value pair of the security headers to be added to response | [optional] 
**jwtSettings** | str,  | str,  | JWT Settings Name | [optional] 
**jwtIssuerSettings** | str,  | str,  | JWT Issuer Settings Name | [optional] 
**[jwtAudiences](#jwtAudiences)** | list, tuple,  | tuple,  | JWT expected Audience list | [optional] 
**disclaimerText** | str,  | str,  | Disclaimer text to be shown to user pre-auth | [optional] 
**idpEntityID** | str,  | str,  | Configure IDP entity for identity bridging | [optional] 
**allowedAudiences** | str,  | str,  | Comma separated values of allowed audiences to be matched againstaudience restriction in the SAML assertion. If empty or not setup then audience restrictions will notbe validated while validating SAML assertion | [optional] 
**radiusUsernameLabel** | str,  | str,  | Customized username label for RADIUS auth screen | [optional] 
**radiusPasscodeLabel** | str,  | str,  | Customized passcode label for RADIUS auth screen | [optional] 
**samlUnauthUsernameAttribute** | str,  | str,  | Attribute to look for in SAML assertion to get Horizon Unauthenticated user | [optional] 
**defaultUnauthUsername** | str,  | str,  | The user name to use for Horizon unauthenticated access | [optional] 
**proxyDestinationPreLoginMessageEnabled** | bool,  | BoolClass,  | Enable or disable connection server pre-login message to be shown to user. Defaults to true | [optional] 
**rewriteOriginHeader** | bool,  | BoolClass,  | Enable origin header rewrite. If enabled the origin header if anyin the request will be rewritten with the hostname present in the Proxy destination URL | [optional] 
**enableClientCertEkuCheck** | bool,  | BoolClass,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

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

# jwtAudiences

JWT expected Audience list

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | JWT expected Audience list | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

