# swagger_client.NetworkSegmentManagementApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_cluster_layer3_segment_health_post**](NetworkSegmentManagementApi.md#v1_cluster_layer3_segment_health_post) | **GET** /v1/cluster/layer3/segment/{segment-label}/health | Get the health status for a segment
[**v1_cluster_layer3_segment_label_delete**](NetworkSegmentManagementApi.md#v1_cluster_layer3_segment_label_delete) | **DELETE** /v1/cluster/layer3/segment/{segment-label} | Delete a segment
[**v1_cluster_layer3_segment_label_get**](NetworkSegmentManagementApi.md#v1_cluster_layer3_segment_label_get) | **GET** /v1/cluster/layer3/segment/{segment-label} | Get the segment configuration for a segment
[**v1_cluster_layer3_segment_label_patch**](NetworkSegmentManagementApi.md#v1_cluster_layer3_segment_label_patch) | **PATCH** /v1/cluster/layer3/segment/{segment-label} | Change the segment label for the current segment
[**v1_cluster_layer3_segment_label_post**](NetworkSegmentManagementApi.md#v1_cluster_layer3_segment_label_post) | **POST** /v1/cluster/layer3/segment/{segment-label} | Update the segment configuration for a segment
[**v1_cluster_layer3_segment_post**](NetworkSegmentManagementApi.md#v1_cluster_layer3_segment_post) | **POST** /v1/cluster/layer3/segment | Create a new segment
[**v1_cluster_layer3_segments_get**](NetworkSegmentManagementApi.md#v1_cluster_layer3_segments_get) | **GET** /v1/cluster/layer3/segments | Get a list of layer 3 segments
[**v2_cluster_layer3_segment_label_delete**](NetworkSegmentManagementApi.md#v2_cluster_layer3_segment_label_delete) | **DELETE** /v2/cluster/layer3/segment/{segment-label} | Delete a segment
[**v2_cluster_layer3_segment_label_get**](NetworkSegmentManagementApi.md#v2_cluster_layer3_segment_label_get) | **GET** /v2/cluster/layer3/segment/{segment-label} | Get the segment configuration for a segment
[**v2_cluster_layer3_segment_label_patch**](NetworkSegmentManagementApi.md#v2_cluster_layer3_segment_label_patch) | **PATCH** /v2/cluster/layer3/segment/{segment-label} | Change the segment label for the current segment
[**v2_cluster_layer3_segment_label_post**](NetworkSegmentManagementApi.md#v2_cluster_layer3_segment_label_post) | **POST** /v2/cluster/layer3/segment/{segment-label} | Update the segment configuration for a segment
[**v2_cluster_layer3_segment_post**](NetworkSegmentManagementApi.md#v2_cluster_layer3_segment_post) | **POST** /v2/cluster/layer3/segment | Create a new segment

# **v1_cluster_layer3_segment_health_post**
> list[SegmentStatusInfo] v1_cluster_layer3_segment_health_post(segment_label)

Get the health status for a segment

Get the health status for a specific segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
segment_label = 'segment_label_example' # str | The label of the segment that you want to query.

try:
    # Get the health status for a segment
    api_response = api_instance.v1_cluster_layer3_segment_health_post(segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v1_cluster_layer3_segment_health_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **segment_label** | **str**| The label of the segment that you want to query. | 

### Return type

[**list[SegmentStatusInfo]**](SegmentStatusInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_layer3_segment_label_delete**
> InlineResponse200 v1_cluster_layer3_segment_label_delete(segment_label)

Delete a segment

Delete a segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
segment_label = 'segment_label_example' # str | The label of the current segment to be acted upon.

try:
    # Delete a segment
    api_response = api_instance.v1_cluster_layer3_segment_label_delete(segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v1_cluster_layer3_segment_label_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **segment_label** | **str**| The label of the current segment to be acted upon. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_layer3_segment_label_get**
> Layer3SegmentSpec v1_cluster_layer3_segment_label_get(segment_label)

Get the segment configuration for a segment

Get the segment configuration for a specified segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
segment_label = 'segment_label_example' # str | The label of the current segment to be acted upon.

try:
    # Get the segment configuration for a segment
    api_response = api_instance.v1_cluster_layer3_segment_label_get(segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v1_cluster_layer3_segment_label_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **segment_label** | **str**| The label of the current segment to be acted upon. | 

### Return type

[**Layer3SegmentSpec**](Layer3SegmentSpec.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_layer3_segment_label_patch**
> InlineResponse200 v1_cluster_layer3_segment_label_patch(body, segment_label)

Change the segment label for the current segment

Change the segment label for the current segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
body = swagger_client.SegmentSegmentlabelBody() # SegmentSegmentlabelBody | The new label that you want the segment to be changed to.
segment_label = 'segment_label_example' # str | The label of the current segment to be acted upon.

try:
    # Change the segment label for the current segment
    api_response = api_instance.v1_cluster_layer3_segment_label_patch(body, segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v1_cluster_layer3_segment_label_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SegmentSegmentlabelBody**](SegmentSegmentlabelBody.md)| The new label that you want the segment to be changed to. | 
 **segment_label** | **str**| The label of the current segment to be acted upon. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_layer3_segment_label_post**
> InlineResponse200 v1_cluster_layer3_segment_label_post(body, segment_label)

Update the segment configuration for a segment

Update the segment configuration for a specific segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
body = swagger_client.Layer3SegmentStartSpec() # Layer3SegmentStartSpec | Information about the segment configuration, including the proxy IP, gateway, netmask, VLAN, and topology.
segment_label = 'segment_label_example' # str | The label of the current segment to be acted upon.

try:
    # Update the segment configuration for a segment
    api_response = api_instance.v1_cluster_layer3_segment_label_post(body, segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v1_cluster_layer3_segment_label_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Layer3SegmentStartSpec**](Layer3SegmentStartSpec.md)| Information about the segment configuration, including the proxy IP, gateway, netmask, VLAN, and topology. | 
 **segment_label** | **str**| The label of the current segment to be acted upon. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_layer3_segment_post**
> InlineResponse200 v1_cluster_layer3_segment_post(body)

Create a new segment

Create a new segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
body = swagger_client.Layer3SegmentStartSpec() # Layer3SegmentStartSpec | Information about the segment configuration, including the proxy IP, gateway, netmask, VLAN, and topology.

try:
    # Create a new segment
    api_response = api_instance.v1_cluster_layer3_segment_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v1_cluster_layer3_segment_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Layer3SegmentStartSpec**](Layer3SegmentStartSpec.md)| Information about the segment configuration, including the proxy IP, gateway, netmask, VLAN, and topology. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_cluster_layer3_segments_get**
> list[str] v1_cluster_layer3_segments_get()

Get a list of layer 3 segments

Get a list of layer 3 segments that are recognized by VxRail Manager.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of layer 3 segments
    api_response = api_instance.v1_cluster_layer3_segments_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v1_cluster_layer3_segments_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**list[str]**

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_cluster_layer3_segment_label_delete**
> InlineResponse200 v2_cluster_layer3_segment_label_delete(segment_label)

Delete a segment

Delete a segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
segment_label = 'segment_label_example' # str | The label of the current segment.

try:
    # Delete a segment
    api_response = api_instance.v2_cluster_layer3_segment_label_delete(segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v2_cluster_layer3_segment_label_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **segment_label** | **str**| The label of the current segment. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_cluster_layer3_segment_label_get**
> Layer3SegmentSpecV2 v2_cluster_layer3_segment_label_get(segment_label)

Get the segment configuration for a segment

Get the segment configuration for a specified segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
segment_label = 'segment_label_example' # str | The label of the current segment.

try:
    # Get the segment configuration for a segment
    api_response = api_instance.v2_cluster_layer3_segment_label_get(segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v2_cluster_layer3_segment_label_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **segment_label** | **str**| The label of the current segment. | 

### Return type

[**Layer3SegmentSpecV2**](Layer3SegmentSpecV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_cluster_layer3_segment_label_patch**
> InlineResponse200 v2_cluster_layer3_segment_label_patch(body, segment_label)

Change the segment label for the current segment

Change the segment label for the current segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
body = swagger_client.SegmentSegmentlabelBody1() # SegmentSegmentlabelBody1 | The new label that you want the segment to be changed to.
segment_label = 'segment_label_example' # str | The label of the current segment.

try:
    # Change the segment label for the current segment
    api_response = api_instance.v2_cluster_layer3_segment_label_patch(body, segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v2_cluster_layer3_segment_label_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SegmentSegmentlabelBody1**](SegmentSegmentlabelBody1.md)| The new label that you want the segment to be changed to. | 
 **segment_label** | **str**| The label of the current segment. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_cluster_layer3_segment_label_post**
> InlineResponse200 v2_cluster_layer3_segment_label_post(body, segment_label)

Update the segment configuration for a segment

Update the segment configuration for a specific segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
body = swagger_client.Layer3SegmentStartSpecV2() # Layer3SegmentStartSpecV2 | Information about the segment configuration, including the proxy IP, gateway, netmask, VLAN, and topology.
segment_label = 'segment_label_example' # str | The label of the current segment.

try:
    # Update the segment configuration for a segment
    api_response = api_instance.v2_cluster_layer3_segment_label_post(body, segment_label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v2_cluster_layer3_segment_label_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Layer3SegmentStartSpecV2**](Layer3SegmentStartSpecV2.md)| Information about the segment configuration, including the proxy IP, gateway, netmask, VLAN, and topology. | 
 **segment_label** | **str**| The label of the current segment. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_cluster_layer3_segment_post**
> InlineResponse200 v2_cluster_layer3_segment_post(body)

Create a new segment

Create a new segment.

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
api_instance = swagger_client.NetworkSegmentManagementApi(swagger_client.ApiClient(configuration))
body = swagger_client.Layer3SegmentStartSpecV2() # Layer3SegmentStartSpecV2 | Information about the segment configuration, including the proxy, management vsan vmotion IP VLAN, and topology.

try:
    # Create a new segment
    api_response = api_instance.v2_cluster_layer3_segment_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling NetworkSegmentManagementApi->v2_cluster_layer3_segment_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Layer3SegmentStartSpecV2**](Layer3SegmentStartSpecV2.md)| Information about the segment configuration, including the proxy, management vsan vmotion IP VLAN, and topology. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

