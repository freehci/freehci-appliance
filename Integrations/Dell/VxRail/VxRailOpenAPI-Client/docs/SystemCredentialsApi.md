# swagger_client.SystemCredentialsApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_system_update_credential_post**](SystemCredentialsApi.md#v1_system_update_credential_post) | **POST** /v1/system/update-credential | Update the management user passwords (v1)
[**v1_system_validate_credential_post**](SystemCredentialsApi.md#v1_system_validate_credential_post) | **POST** /v1/system/validate-credential | Validate the supplied user credentials
[**v2_system_update_credential_post**](SystemCredentialsApi.md#v2_system_update_credential_post) | **POST** /v2/system/update-credential | Update the management user passwords (v2)

# **v1_system_update_credential_post**
> v1_system_update_credential_post(body)

Update the management user passwords (v1)

Update management user passwords that are stored in VxRail Manager for the specified ESXi hosts.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: basicAuth
configuration = swagger_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = swagger_client.SystemCredentialsApi(swagger_client.ApiClient(configuration))
body = [swagger_client.AccountCredential()] # list[AccountCredential] | The management account information needed for updating passwords

try:
    # Update the management user passwords (v1)
    api_instance.v1_system_update_credential_post(body)
except ApiException as e:
    print("Exception when calling SystemCredentialsApi->v1_system_update_credential_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[AccountCredential]**](AccountCredential.md)| The management account information needed for updating passwords | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_validate_credential_post**
> v1_system_validate_credential_post(body)

Validate the supplied user credentials

Validate the username and password for the specified software components.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: basicAuth
configuration = swagger_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = swagger_client.SystemCredentialsApi(swagger_client.ApiClient(configuration))
body = swagger_client.SystemValidatecredentialBody() # SystemValidatecredentialBody | Credentials that you input for validation.

try:
    # Validate the supplied user credentials
    api_instance.v1_system_validate_credential_post(body)
except ApiException as e:
    print("Exception when calling SystemCredentialsApi->v1_system_validate_credential_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SystemValidatecredentialBody**](SystemValidatecredentialBody.md)| Credentials that you input for validation. | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_system_update_credential_post**
> v2_system_update_credential_post(body)

Update the management user passwords (v2)

Update the management user passwords that are stored in VxRail Manager for the vCenter and ESXi hosts.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: basicAuth
configuration = swagger_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = swagger_client.SystemCredentialsApi(swagger_client.ApiClient(configuration))
body = [swagger_client.AccountCredentialV2()] # list[AccountCredentialV2] | The management account information needed for updating passwords

try:
    # Update the management user passwords (v2)
    api_instance.v2_system_update_credential_post(body)
except ApiException as e:
    print("Exception when calling SystemCredentialsApi->v2_system_update_credential_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[AccountCredentialV2]**](AccountCredentialV2.md)| The management account information needed for updating passwords | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

