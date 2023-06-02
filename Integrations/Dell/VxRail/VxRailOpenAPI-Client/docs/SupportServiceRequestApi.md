# swagger_client.SupportServiceRequestApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_support_service_requests_get**](SupportServiceRequestApi.md#v1_support_service_requests_get) | **GET** /v1/support/service-requests | Get links for opening Service Requests

# **v1_support_service_requests_get**
> list[ServiceRequestInfo] v1_support_service_requests_get()

Get links for opening Service Requests

Get links for opening Service Requests (SRs). One link per node.

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
api_instance = swagger_client.SupportServiceRequestApi(swagger_client.ApiClient(configuration))

try:
    # Get links for opening Service Requests
    api_response = api_instance.v1_support_service_requests_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportServiceRequestApi->v1_support_service_requests_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ServiceRequestInfo]**](ServiceRequestInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

