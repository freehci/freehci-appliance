# swagger_client.ClusterShutdownApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_cluster_shutdown_post**](ClusterShutdownApi.md#v1_cluster_shutdown_post) | **POST** /v1/cluster/shutdown | Shut down a cluster or perform a shutdown dry run

# **v1_cluster_shutdown_post**
> InlineResponse202 v1_cluster_shutdown_post(body=body)

Shut down a cluster or perform a shutdown dry run

Shut down a cluster or perform a shutdown dry run.

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
api_instance = swagger_client.ClusterShutdownApi(swagger_client.ApiClient(configuration))
body = swagger_client.ClusterShutdownBody() # ClusterShutdownBody | Perform an optional dry run to check whether it is safe to shut down. The default value is false. (optional)

try:
    # Shut down a cluster or perform a shutdown dry run
    api_response = api_instance.v1_cluster_shutdown_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClusterShutdownApi->v1_cluster_shutdown_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ClusterShutdownBody**](ClusterShutdownBody.md)| Perform an optional dry run to check whether it is safe to shut down. The default value is false. | [optional] 

### Return type

[**InlineResponse202**](InlineResponse202.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

