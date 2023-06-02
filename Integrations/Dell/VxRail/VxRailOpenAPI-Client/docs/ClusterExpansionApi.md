# swagger_client.ClusterExpansionApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_cluster_expansion_cancel_post**](ClusterExpansionApi.md#v1_cluster_expansion_cancel_post) | **POST** /v1/cluster/expansion/cancel | Cancel a failed cluster expansion
[**v1_cluster_expansion_post**](ClusterExpansionApi.md#v1_cluster_expansion_post) | **POST** /v1/cluster/expansion | Perform a cluster expansion
[**v1_cluster_expansion_validate_post**](ClusterExpansionApi.md#v1_cluster_expansion_validate_post) | **POST** /v1/cluster/expansion/validate | Validate a cluster expansion

# **v1_cluster_expansion_cancel_post**
> v1_cluster_expansion_cancel_post()

Cancel a failed cluster expansion

Cancel a failed cluster expansion.

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
api_instance = swagger_client.ClusterExpansionApi(swagger_client.ApiClient(configuration))

try:
    # Cancel a failed cluster expansion
    api_instance.v1_cluster_expansion_cancel_post()
except ApiException as e:
    print("Exception when calling ClusterExpansionApi->v1_cluster_expansion_cancel_post: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_expansion_post**
> ExpansionNodeInfo v1_cluster_expansion_post(body)

Perform a cluster expansion

Perform a cluster expansion (layer 2 or layer 3) based on the provided expansion specification.

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
api_instance = swagger_client.ClusterExpansionApi(swagger_client.ApiClient(configuration))
body = swagger_client.ExpansionRequest() # ExpansionRequest | Parameters to perform the cluster expansion.

try:
    # Perform a cluster expansion
    api_response = api_instance.v1_cluster_expansion_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClusterExpansionApi->v1_cluster_expansion_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ExpansionRequest**](ExpansionRequest.md)| Parameters to perform the cluster expansion. | 

### Return type

[**ExpansionNodeInfo**](ExpansionNodeInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_expansion_validate_post**
> ExpansionNodeInfo v1_cluster_expansion_validate_post(body)

Validate a cluster expansion

Validate a cluster expansion (layer 2 or layer 3) based on the provided expansion specification.

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
api_instance = swagger_client.ClusterExpansionApi(swagger_client.ApiClient(configuration))
body = swagger_client.ExpansionRequest() # ExpansionRequest | Parameters to validate the cluster expansion.

try:
    # Validate a cluster expansion
    api_response = api_instance.v1_cluster_expansion_validate_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClusterExpansionApi->v1_cluster_expansion_validate_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ExpansionRequest**](ExpansionRequest.md)| Parameters to validate the cluster expansion. | 

### Return type

[**ExpansionNodeInfo**](ExpansionNodeInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

