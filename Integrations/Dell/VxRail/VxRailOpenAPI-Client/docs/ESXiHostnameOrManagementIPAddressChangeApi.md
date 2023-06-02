# swagger_client.ESXiHostnameOrManagementIPAddressChangeApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**request_get**](ESXiHostnameOrManagementIPAddressChangeApi.md#request_get) | **GET** /requests/{requestId_sample_reHostname} | 

# **request_get**
> RequestStatusInfo request_get(request_id_sample_re_hostname)



Retrieves the operation status and progress report.

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
api_instance = swagger_client.ESXiHostnameOrManagementIPAddressChangeApi(swagger_client.ApiClient(configuration))
request_id_sample_re_hostname = 'request_id_sample_re_hostname_example' # str | The request ID of any long running operation.

try:
    api_response = api_instance.request_get(request_id_sample_re_hostname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ESXiHostnameOrManagementIPAddressChangeApi->request_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id_sample_re_hostname** | **str**| The request ID of any long running operation. | 

### Return type

[**RequestStatusInfo**](RequestStatusInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

