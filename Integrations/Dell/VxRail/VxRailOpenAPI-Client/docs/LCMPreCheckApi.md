# swagger_client.LCMPreCheckApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**precheck_v1**](LCMPreCheckApi.md#precheck_v1) | **POST** /v1/lcm/precheck | Perform a health pre-check

# **precheck_v1**
> AsyncLcmRequestSuccessResponse precheck_v1(body)

Perform a health pre-check

Perform a separate health pre-check for the VxRail system.

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
api_instance = swagger_client.LCMPreCheckApi(swagger_client.ApiClient(configuration))
body = swagger_client.HealthPrecheckSpecV1() # HealthPrecheckSpecV1 | Input parameters needed for health pre-check

try:
    # Perform a health pre-check
    api_response = api_instance.precheck_v1(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMPreCheckApi->precheck_v1: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HealthPrecheckSpecV1**](HealthPrecheckSpecV1.md)| Input parameters needed for health pre-check | 

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

