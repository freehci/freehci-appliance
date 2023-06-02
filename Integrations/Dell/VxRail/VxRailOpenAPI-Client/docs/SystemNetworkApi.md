# swagger_client.SystemNetworkApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_system_cluster_portgroups_fqdn_get**](SystemNetworkApi.md#v1_system_cluster_portgroups_fqdn_get) | **GET** /v1/system/cluster-portgroups/{node_fqdn} | Get information about cluster portgroups
[**v1_system_cluster_portgroups_get**](SystemNetworkApi.md#v1_system_cluster_portgroups_get) | **GET** /v1/system/cluster-portgroups | Get information about cluster portgroups
[**v1_system_internet_mode_get**](SystemNetworkApi.md#v1_system_internet_mode_get) | **GET** /v1/system/internet-mode | Get VxRail system network status
[**v1_system_internet_mode_put**](SystemNetworkApi.md#v1_system_internet_mode_put) | **PUT** /v1/system/internet-mode | Update the VxRail system network parameters

# **v1_system_cluster_portgroups_fqdn_get**
> list[ClusterPortgroup] v1_system_cluster_portgroups_fqdn_get(node_fqdn)

Get information about cluster portgroups

Get information about cluster portgroups used by a node.

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
api_instance = swagger_client.SystemNetworkApi(swagger_client.ApiClient(configuration))
node_fqdn = 'node_fqdn_example' # str | The FQDN of the node that you want to query

try:
    # Get information about cluster portgroups
    api_response = api_instance.v1_system_cluster_portgroups_fqdn_get(node_fqdn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemNetworkApi->v1_system_cluster_portgroups_fqdn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_fqdn** | **str**| The FQDN of the node that you want to query | 

### Return type

[**list[ClusterPortgroup]**](ClusterPortgroup.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_cluster_portgroups_get**
> list[ClusterPortgroup] v1_system_cluster_portgroups_get(node_fqdn)

Get information about cluster portgroups

Get information about cluster portgroups used by a node. You specify the node using a query parameter.

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
api_instance = swagger_client.SystemNetworkApi(swagger_client.ApiClient(configuration))
node_fqdn = 'node_fqdn_example' # str | The FQDN of the node that you want to query

try:
    # Get information about cluster portgroups
    api_response = api_instance.v1_system_cluster_portgroups_get(node_fqdn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemNetworkApi->v1_system_cluster_portgroups_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_fqdn** | **str**| The FQDN of the node that you want to query | 

### Return type

[**list[ClusterPortgroup]**](ClusterPortgroup.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_internet_mode_get**
> InternetMode v1_system_internet_mode_get()

Get VxRail system network status

Get VxRail system network status.

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
api_instance = swagger_client.SystemNetworkApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail system network status
    api_response = api_instance.v1_system_internet_mode_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemNetworkApi->v1_system_internet_mode_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InternetMode**](InternetMode.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_internet_mode_put**
> v1_system_internet_mode_put(body)

Update the VxRail system network parameters

Update the VxRail system network parameters.

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
api_instance = swagger_client.SystemNetworkApi(swagger_client.ApiClient(configuration))
body = swagger_client.InternetMode() # InternetMode | Configure VxRail system network mode to darksite or not

try:
    # Update the VxRail system network parameters
    api_instance.v1_system_internet_mode_put(body)
except ApiException as e:
    print("Exception when calling SystemNetworkApi->v1_system_internet_mode_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**InternetMode**](InternetMode.md)| Configure VxRail system network mode to darksite or not | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

