# swagger_client.SupportHeartbeatInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_support_heartbeat_get**](SupportHeartbeatInformationApi.md#v1_support_heartbeat_get) | **GET** /v1/support/heartbeat | Get the last heartbeat status

# **v1_support_heartbeat_get**
> HeartbeatInfo v1_support_heartbeat_get()

Get the last heartbeat status

Get the last heartbeat status and system configuration.

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
api_instance = swagger_client.SupportHeartbeatInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get the last heartbeat status
    api_response = api_instance.v1_support_heartbeat_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportHeartbeatInformationApi->v1_support_heartbeat_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**HeartbeatInfo**](HeartbeatInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

