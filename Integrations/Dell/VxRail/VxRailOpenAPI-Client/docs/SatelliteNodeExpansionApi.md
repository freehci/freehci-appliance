# swagger_client.SatelliteNodeExpansionApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**remove_satellite_host**](SatelliteNodeExpansionApi.md#remove_satellite_host) | **DELETE** /v1/host-folder/hosts/{sn} | remove a satellite node from the host folder
[**v1_satellite_node_expansion_cancel_post**](SatelliteNodeExpansionApi.md#v1_satellite_node_expansion_cancel_post) | **POST** /v1/host-folder/expansion/cancel | Cancel a failed satellite node expansion
[**v1_satellite_node_expansion_post**](SatelliteNodeExpansionApi.md#v1_satellite_node_expansion_post) | **POST** /v1/host-folder/expansion | Perform a satellite node expansion

# **remove_satellite_host**
> remove_satellite_host(sn)

remove a satellite node from the host folder

Satellite node removal. Remove a satellite node from a VxRail-managed folder.

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
api_instance = swagger_client.SatelliteNodeExpansionApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | serial number of target host

try:
    # remove a satellite node from the host folder
    api_instance.remove_satellite_host(sn)
except ApiException as e:
    print("Exception when calling SatelliteNodeExpansionApi->remove_satellite_host: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| serial number of target host | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_satellite_node_expansion_cancel_post**
> v1_satellite_node_expansion_cancel_post()

Cancel a failed satellite node expansion

Cancel a failed satellite node expansion.

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
api_instance = swagger_client.SatelliteNodeExpansionApi(swagger_client.ApiClient(configuration))

try:
    # Cancel a failed satellite node expansion
    api_instance.v1_satellite_node_expansion_cancel_post()
except ApiException as e:
    print("Exception when calling SatelliteNodeExpansionApi->v1_satellite_node_expansion_cancel_post: %s\n" % e)
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

# **v1_satellite_node_expansion_post**
> ExpansionNodeInfo v1_satellite_node_expansion_post(body)

Perform a satellite node expansion

Perform a satellite node expansion based on the provided expansion specification.

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
api_instance = swagger_client.SatelliteNodeExpansionApi(swagger_client.ApiClient(configuration))
body = swagger_client.SatelliteNodeExpansionSpec() # SatelliteNodeExpansionSpec | Parameters to perform the satellite node expansion.

try:
    # Perform a satellite node expansion
    api_response = api_instance.v1_satellite_node_expansion_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SatelliteNodeExpansionApi->v1_satellite_node_expansion_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SatelliteNodeExpansionSpec**](SatelliteNodeExpansionSpec.md)| Parameters to perform the satellite node expansion. | 

### Return type

[**ExpansionNodeInfo**](ExpansionNodeInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

