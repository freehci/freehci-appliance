# swagger_client.CallHomeModeApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_callhome_mode_get**](CallHomeModeApi.md#v1_callhome_mode_get) | **GET** /v1/callhome/mode | Get call home mode
[**v1_callhome_mode_put**](CallHomeModeApi.md#v1_callhome_mode_put) | **PUT** /v1/callhome/mode | Change call home mode

# **v1_callhome_mode_get**
> CallhomeSettingsInfo v1_callhome_mode_get()

Get call home mode

Retrieve the call home mode.

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
api_instance = swagger_client.CallHomeModeApi(swagger_client.ApiClient(configuration))

try:
    # Get call home mode
    api_response = api_instance.v1_callhome_mode_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeModeApi->v1_callhome_mode_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**CallhomeSettingsInfo**](CallhomeSettingsInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_callhome_mode_put**
> v1_callhome_mode_put(body)

Change call home mode

Change the call home mode.

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
api_instance = swagger_client.CallHomeModeApi(swagger_client.ApiClient(configuration))
body = swagger_client.CallhomeSettingsSpec() # CallhomeSettingsSpec | Sets whether call home mode is muted or unmuted.

try:
    # Change call home mode
    api_instance.v1_callhome_mode_put(body)
except ApiException as e:
    print("Exception when calling CallHomeModeApi->v1_callhome_mode_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CallhomeSettingsSpec**](CallhomeSettingsSpec.md)| Sets whether call home mode is muted or unmuted. | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

