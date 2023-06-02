# swagger_client.HostFolderLCMApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_lcm_folders_upgrade**](HostFolderLCMApi.md#v1_lcm_folders_upgrade) | **POST** /v1/lcm/host-folder/upgrade | Perform host folder LCM

# **v1_lcm_folders_upgrade**
> InlineResponse202 v1_lcm_folders_upgrade(body)

Perform host folder LCM

Perform node upgrade for all eligible satellite nodes in the specific host folder

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
api_instance = swagger_client.HostFolderLCMApi(swagger_client.ApiClient(configuration))
body = swagger_client.HostFolderLCMSpec() # HostFolderLCMSpec | Parameters to perform host folder LCM.

try:
    # Perform host folder LCM
    api_response = api_instance.v1_lcm_folders_upgrade(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostFolderLCMApi->v1_lcm_folders_upgrade: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HostFolderLCMSpec**](HostFolderLCMSpec.md)| Parameters to perform host folder LCM. | 

### Return type

[**InlineResponse202**](InlineResponse202.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

