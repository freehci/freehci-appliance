# swagger_client.SupportLogsApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_support_logs_get**](SupportLogsApi.md#v1_support_logs_get) | **GET** /v1/support/logs | Query all of support logs
[**v1_support_logs_id_download_get**](SupportLogsApi.md#v1_support_logs_id_download_get) | **GET** /v1/support/logs/{logId}/download | Download the binary stream of a log
[**v1_support_logs_id_get**](SupportLogsApi.md#v1_support_logs_id_get) | **GET** /v1/support/logs/{logId} | Query the log by the log ID
[**v1_support_logs_post**](SupportLogsApi.md#v1_support_logs_post) | **POST** /v1/support/logs | Collect the support log with the specified types of components

# **v1_support_logs_get**
> list[LogInfo] v1_support_logs_get(filter=filter)

Query all of support logs

Query all of the support logs.

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
api_instance = swagger_client.SupportLogsApi(swagger_client.ApiClient(configuration))
filter = 'filter_example' # str | Query conditions for the support logs. Equal(eq), and not equal(ne) supported fields: id, path, types, nodes. In addition, types and nodes are collection condition fields, which mean the value is equal though the sequence is different. For example, 'node1, node2, node3' is equal to 'node3, node2, node1'. Example: $filter=id eq 'VxRail_Support_Bundle_52fd1cfc-4646-8a7d-d4ba-721c3da3808e_2018_10_08_08_30_44 and nodes eq 'node1, node2, node3' (optional)

try:
    # Query all of support logs
    api_response = api_instance.v1_support_logs_get(filter=filter)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportLogsApi->v1_support_logs_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| Query conditions for the support logs. Equal(eq), and not equal(ne) supported fields: id, path, types, nodes. In addition, types and nodes are collection condition fields, which mean the value is equal though the sequence is different. For example, &#x27;node1, node2, node3&#x27; is equal to &#x27;node3, node2, node1&#x27;. Example: $filter&#x3D;id eq &#x27;VxRail_Support_Bundle_52fd1cfc-4646-8a7d-d4ba-721c3da3808e_2018_10_08_08_30_44 and nodes eq &#x27;node1, node2, node3&#x27; | [optional] 

### Return type

[**list[LogInfo]**](LogInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_support_logs_id_download_get**
> Componentsresponses200 v1_support_logs_id_download_get(log_id)

Download the binary stream of a log

Download the binary stream of a log.

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
api_instance = swagger_client.SupportLogsApi(swagger_client.ApiClient(configuration))
log_id = 'log_id_example' # str | The unique identifier of the log that you want to download.

try:
    # Download the binary stream of a log
    api_response = api_instance.v1_support_logs_id_download_get(log_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportLogsApi->v1_support_logs_id_download_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **log_id** | **str**| The unique identifier of the log that you want to download. | 

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_support_logs_id_get**
> LogInfo v1_support_logs_id_get(log_id)

Query the log by the log ID

Query the log by the log ID.

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
api_instance = swagger_client.SupportLogsApi(swagger_client.ApiClient(configuration))
log_id = 'log_id_example' # str | The log ID

try:
    # Query the log by the log ID
    api_response = api_instance.v1_support_logs_id_get(log_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportLogsApi->v1_support_logs_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **log_id** | **str**| The log ID | 

### Return type

[**LogInfo**](LogInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_support_logs_post**
> InlineResponse202 v1_support_logs_post(body)

Collect the support log with the specified types of components

Collect the support log with the specified types of components.

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
api_instance = swagger_client.SupportLogsApi(swagger_client.ApiClient(configuration))
body = swagger_client.LogSpec() # LogSpec | The specified types and nodes for the log bundle collection.

try:
    # Collect the support log with the specified types of components
    api_response = api_instance.v1_support_logs_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportLogsApi->v1_support_logs_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LogSpec**](LogSpec.md)| The specified types and nodes for the log bundle collection. | 

### Return type

[**InlineResponse202**](InlineResponse202.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

