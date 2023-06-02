# swagger_client.RequestStatusApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_request_id_get**](RequestStatusApi.md#v1_request_id_get) | **GET** /v1/requests/{id} | Get the status of a request
[**v1_requests_get**](RequestStatusApi.md#v1_requests_get) | **GET** /v1/requests | Query all requests

# **v1_request_id_get**
> RequestStatusInfo v1_request_id_get(id)

Get the status of a request

Retrieve the operation status and progress report of the specified request.

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
api_instance = swagger_client.RequestStatusApi(swagger_client.ApiClient(configuration))
id = 'id_example' # str | The request ID of any long running operation.

try:
    # Get the status of a request
    api_response = api_instance.v1_request_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RequestStatusApi->v1_request_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The request ID of any long running operation. | 

### Return type

[**RequestStatusInfo**](RequestStatusInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_requests_get**
> list[RequestStatusInfo] v1_requests_get(filter=filter)

Query all requests

Query all of the requests.

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
api_instance = swagger_client.RequestStatusApi(swagger_client.ApiClient(configuration))
filter = 'filter_example' # str | Query condictions for requests. Equal(eq), in(in) and not equal(ne) supported fields: id, state, owner, target, step. Equal(eq), not equal(ne), in(in), greater than(gt), less than(lt), greater or equal to(ge) and less or equal to(le) supported fields: start_time, end_time, progress. Example: $filter=id eq 'e9082a79-12c8-484f-9b11-76c1a6e2f36b' and owner eq 'LOG_BUNDLE' and state in ('FAILED','IN_PROGRESS') and start_time gt 10000. (optional)

try:
    # Query all requests
    api_response = api_instance.v1_requests_get(filter=filter)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RequestStatusApi->v1_requests_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| Query condictions for requests. Equal(eq), in(in) and not equal(ne) supported fields: id, state, owner, target, step. Equal(eq), not equal(ne), in(in), greater than(gt), less than(lt), greater or equal to(ge) and less or equal to(le) supported fields: start_time, end_time, progress. Example: $filter&#x3D;id eq &#x27;e9082a79-12c8-484f-9b11-76c1a6e2f36b&#x27; and owner eq &#x27;LOG_BUNDLE&#x27; and state in (&#x27;FAILED&#x27;,&#x27;IN_PROGRESS&#x27;) and start_time gt 10000. | [optional] 

### Return type

[**list[RequestStatusInfo]**](RequestStatusInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

