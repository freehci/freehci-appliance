# swagger_client.SupportChatApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_support_chat_url_get**](SupportChatApi.md#v1_support_chat_url_get) | **GET** /v1/support/chat-url | Get a URL to start a chat session with a Dell Support

# **v1_support_chat_url_get**
> ChatInfo v1_support_chat_url_get()

Get a URL to start a chat session with a Dell Support

Get a URL link to start a chat session with a support representative.

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
api_instance = swagger_client.SupportChatApi(swagger_client.ApiClient(configuration))

try:
    # Get a URL to start a chat session with a Dell Support
    api_response = api_instance.v1_support_chat_url_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportChatApi->v1_support_chat_url_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ChatInfo**](ChatInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

