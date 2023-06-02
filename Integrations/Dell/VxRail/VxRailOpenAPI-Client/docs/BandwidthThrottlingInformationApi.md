# swagger_client.BandwidthThrottlingInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_v1_system_bandwidth_throttling**](BandwidthThrottlingInformationApi.md#get_v1_system_bandwidth_throttling) | **GET** /v1/system/bandwidth-throttling | Get bandwidth throttling information
[**put_v1_system_bandwidth_throttling**](BandwidthThrottlingInformationApi.md#put_v1_system_bandwidth_throttling) | **PUT** /v1/system/bandwidth-throttling | Update bandwidth throttling information

# **get_v1_system_bandwidth_throttling**
> BandwidthThrottlingInfo get_v1_system_bandwidth_throttling()

Get bandwidth throttling information

Get bandwidth throttling information

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
api_instance = swagger_client.BandwidthThrottlingInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get bandwidth throttling information
    api_response = api_instance.get_v1_system_bandwidth_throttling()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BandwidthThrottlingInformationApi->get_v1_system_bandwidth_throttling: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**BandwidthThrottlingInfo**](BandwidthThrottlingInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_v1_system_bandwidth_throttling**
> put_v1_system_bandwidth_throttling(body=body)

Update bandwidth throttling information

Update bandwidth throttling information

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
api_instance = swagger_client.BandwidthThrottlingInformationApi(swagger_client.ApiClient(configuration))
body = swagger_client.BandwidthThrottlingInfo() # BandwidthThrottlingInfo | Bandwidth throttling level (optional)

try:
    # Update bandwidth throttling information
    api_instance.put_v1_system_bandwidth_throttling(body=body)
except ApiException as e:
    print("Exception when calling BandwidthThrottlingInformationApi->put_v1_system_bandwidth_throttling: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BandwidthThrottlingInfo**](BandwidthThrottlingInfo.md)| Bandwidth throttling level | [optional] 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

