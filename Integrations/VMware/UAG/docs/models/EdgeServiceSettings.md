# openapi_client.model.edge_service_settings.EdgeServiceSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**identifier** | str,  | str,  | The type of edge service. | 
**enabled** | bool,  | BoolClass,  | Whether this service is enabled | 
**proxyDestinationUrl** | str,  | str,  | Users will make HTTP requests to the Access Point to access a service, and the requests will be proxied to this URL, where the service lives. | [optional] 
**proxyDestinationUrlThumbprints** | str,  | str,  | List of acceptable SSL server certificate thumbprints for the proxyDestinationUrl. If blank, a valid certificate is required. If &#x27;*&#x27;, any certificate is allowed. Otherwise, this is a comma-separated list of thumbprints. A thumbprint is of the format [alg&#x3D;]xx:xx... where alg can be sha1(default) or md5 and the &#x27;xx&#x27; are hexidecimal digits. The &#x27;:&#x27; separator can also be a space or missing. Case in a thumbprint is ignored. | [optional] 
**authMethods** | str,  | str,  | Comma-separated list of the names of authentication methods to use for the edge service. If blank or null, no AP authentication is enforced. | [optional] 
**healthCheckUrl** | str,  | str,  | Health check url to be used to check health of the backend. If notprovided /favicon.ico will be used | [optional] 
**samlSP** | str,  | str,  | The name of the SAML service provider for the View XMLAPI broker. This name must either match the name of a configured service provider metadata or be the special value \&quot;DEMO\&quot;. | [optional] 
**[hostEntries](#hostEntries)** | list, tuple,  | tuple,  | The list of host entries to be added in /etc/hosts/ | [optional] 
**[trustedCertificates](#trustedCertificates)** | list, tuple,  | tuple,  | The list of trusted certificates to be added in /etc/pki/trust/anchors/ | [optional] 
**devicePolicyServiceProvider** | str,  | str,  | Name of the device policy check service provider. | [optional] must be one of ["OPSWAT", "Workspace_ONE_Intelligence_Risk_Score", ] 
**[customExecutableList](#customExecutableList)** | list, tuple,  | tuple,  | List of custom executables | [optional] 
**redirectHostPortMappingList** | str,  | str,  | Comma seperated values of source host:port to redirect host:port. Port is optional, 443 is assumed by default. Host and port should be separated with a colon (:). Each entry should be in source-host[:port]_redirect-host[:port] format eg: extrenalhost1.com_uag1.com, externalhost2.com_uag1.com, externalhost3.com:12443_uag3.com:12443 | [optional] 
**canonicalizationEnabled** | bool,  | BoolClass,  | The default value is true for horizon and false for web reverse proxy | [optional] 
**hostRedirectionEnabled** | bool,  | BoolClass,  | This configuration is required for the handling for redirection response from the backend service, Although introduced for Horizon broker use case, but it is not tied to Horizon broker and can be used for the WRP use cases as well. | [optional] 
**uniqueInstanceId** | str,  | str,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# hostEntries

The list of host entries to be added in /etc/hosts/

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | The list of host entries to be added in /etc/hosts/ | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | 

# trustedCertificates

The list of trusted certificates to be added in /etc/pki/trust/anchors/

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | The list of trusted certificates to be added in /etc/pki/trust/anchors/ | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) | [**PublicKeyOrCert**](PublicKeyOrCert.md) |  | 

# customExecutableList

List of custom executables

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of custom executables | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

