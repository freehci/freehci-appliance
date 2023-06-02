# swagger_client.SystemProxySettingsApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_system_proxy_delete**](SystemProxySettingsApi.md#v1_system_proxy_delete) | **DELETE** /v1/system/proxy | Disable VxRail Manager system proxy settings
[**v1_system_proxy_get**](SystemProxySettingsApi.md#v1_system_proxy_get) | **GET** /v1/system/proxy | Get the VxRail Manager system proxy settings
[**v1_system_proxy_patch**](SystemProxySettingsApi.md#v1_system_proxy_patch) | **PATCH** /v1/system/proxy | Update VxRail Manager system proxy settings
[**v1_system_proxy_post**](SystemProxySettingsApi.md#v1_system_proxy_post) | **POST** /v1/system/proxy | Enable VxRail Manager system proxy settings

# **v1_system_proxy_delete**
> v1_system_proxy_delete(body=body)

Disable VxRail Manager system proxy settings

Disable VxRail Manager system proxy settings.

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
api_instance = swagger_client.SystemProxySettingsApi(swagger_client.ApiClient(configuration))
body = swagger_client.SystemProxyBody() # SystemProxyBody | Password for Secure Remote Services (SRS) (optional)

try:
    # Disable VxRail Manager system proxy settings
    api_instance.v1_system_proxy_delete(body=body)
except ApiException as e:
    print("Exception when calling SystemProxySettingsApi->v1_system_proxy_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SystemProxyBody**](SystemProxyBody.md)| Password for Secure Remote Services (SRS) | [optional] 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_proxy_get**
> ProxySettings v1_system_proxy_get()

Get the VxRail Manager system proxy settings

Get the VxRail Manager system proxy settings.

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
api_instance = swagger_client.SystemProxySettingsApi(swagger_client.ApiClient(configuration))

try:
    # Get the VxRail Manager system proxy settings
    api_response = api_instance.v1_system_proxy_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemProxySettingsApi->v1_system_proxy_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ProxySettings**](ProxySettings.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_proxy_patch**
> v1_system_proxy_patch(body)

Update VxRail Manager system proxy settings

Update VxRail Manager system proxy settings.

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
api_instance = swagger_client.SystemProxySettingsApi(swagger_client.ApiClient(configuration))
body = swagger_client.ProxySettingsSpec() # ProxySettingsSpec | Configurable parameters to set and update for the proxy server.

try:
    # Update VxRail Manager system proxy settings
    api_instance.v1_system_proxy_patch(body)
except ApiException as e:
    print("Exception when calling SystemProxySettingsApi->v1_system_proxy_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ProxySettingsSpec**](ProxySettingsSpec.md)| Configurable parameters to set and update for the proxy server. | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_proxy_post**
> v1_system_proxy_post(body)

Enable VxRail Manager system proxy settings

Enable VxRail Manager system proxy settings.

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
api_instance = swagger_client.SystemProxySettingsApi(swagger_client.ApiClient(configuration))
body = swagger_client.ProxySettingsSpec() # ProxySettingsSpec | Configurable parameters for the proxy server

try:
    # Enable VxRail Manager system proxy settings
    api_instance.v1_system_proxy_post(body)
except ApiException as e:
    print("Exception when calling SystemProxySettingsApi->v1_system_proxy_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ProxySettingsSpec**](ProxySettingsSpec.md)| Configurable parameters for the proxy server | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

