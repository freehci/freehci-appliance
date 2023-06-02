# swagger_client.ClusterInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_cluster_get**](ClusterInformationApi.md#v1_cluster_get) | **GET** /v1/cluster | Get VxRail cluster information
[**v2_cluster_get**](ClusterInformationApi.md#v2_cluster_get) | **GET** /v2/cluster | Get VxRail cluster information

# **v1_cluster_get**
> ClusterInfo v1_cluster_get()

Get VxRail cluster information

Get VxRail cluster information and basic information about the appliances in the cluster.

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
api_instance = swagger_client.ClusterInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail cluster information
    api_response = api_instance.v1_cluster_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClusterInformationApi->v1_cluster_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ClusterInfo**](ClusterInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_cluster_get**
> ClusterInfoV2 v2_cluster_get()

Get VxRail cluster information

Get VxRail cluster information and basic information about the appliances in the cluster.

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
api_instance = swagger_client.ClusterInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail cluster information
    api_response = api_instance.v2_cluster_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClusterInformationApi->v2_cluster_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ClusterInfoV2**](ClusterInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

