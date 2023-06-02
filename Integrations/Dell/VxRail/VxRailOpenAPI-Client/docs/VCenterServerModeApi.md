# swagger_client.VCenterServerModeApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_vc_vc_mode_get**](VCenterServerModeApi.md#v1_vc_vc_mode_get) | **GET** /v1/vc/mode | Get the vCenter and Platform Services Controller mode
[**v1_vc_vc_mode_patch**](VCenterServerModeApi.md#v1_vc_vc_mode_patch) | **PATCH** /v1/vc/mode | Change the vCenter and Platform Services Controller mode

# **v1_vc_vc_mode_get**
> ClusterModeInfo v1_vc_vc_mode_get()

Get the vCenter and Platform Services Controller mode

Get the current vCenter mode and Platform Services Controller (PSC) mode.

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
api_instance = swagger_client.VCenterServerModeApi(swagger_client.ApiClient(configuration))

try:
    # Get the vCenter and Platform Services Controller mode
    api_response = api_instance.v1_vc_vc_mode_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VCenterServerModeApi->v1_vc_vc_mode_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ClusterModeInfo**](ClusterModeInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_vc_vc_mode_patch**
> Model202Nocontent v1_vc_vc_mode_patch(body)

Change the vCenter and Platform Services Controller mode

Change the VxRail vCenter or Platform Services Controller (PSC) mode between embedded mode and external mode.

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
api_instance = swagger_client.VCenterServerModeApi(swagger_client.ApiClient(configuration))
body = swagger_client.VcConversionSpec() # VcConversionSpec | Information needed to update the vCenter or PSC mode to embedded or external.

try:
    # Change the vCenter and Platform Services Controller mode
    api_response = api_instance.v1_vc_vc_mode_patch(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VCenterServerModeApi->v1_vc_vc_mode_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VcConversionSpec**](VcConversionSpec.md)| Information needed to update the vCenter or PSC mode to embedded or external. | 

### Return type

[**Model202Nocontent**](Model202Nocontent.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

