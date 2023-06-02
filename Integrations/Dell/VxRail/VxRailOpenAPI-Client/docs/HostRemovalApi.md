# swagger_client.HostRemovalApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_cluster_remove_host_post**](HostRemovalApi.md#v1_cluster_remove_host_post) | **POST** /v1/cluster/remove-host | Remove a host from the cluster

# **v1_cluster_remove_host_post**
> InlineResponse202 v1_cluster_remove_host_post(body)

Remove a host from the cluster

Remove a host from the cluster.

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
api_instance = swagger_client.HostRemovalApi(swagger_client.ApiClient(configuration))
body = swagger_client.RemoveHostSpec() # RemoveHostSpec | The user-specified host to be removed

try:
    # Remove a host from the cluster
    api_response = api_instance.v1_cluster_remove_host_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostRemovalApi->v1_cluster_remove_host_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**RemoveHostSpec**](RemoveHostSpec.md)| The user-specified host to be removed | 

### Return type

[**InlineResponse202**](InlineResponse202.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

