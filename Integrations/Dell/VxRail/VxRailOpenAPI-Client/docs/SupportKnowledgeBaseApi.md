# swagger_client.SupportKnowledgeBaseApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_kb_articels_get**](SupportKnowledgeBaseApi.md#v1_kb_articels_get) | **GET** /v1/support/kb/articles | Get articles from the Support Knowledge Base
[**v1_kb_get**](SupportKnowledgeBaseApi.md#v1_kb_get) | **GET** /v1/support/kb | Get the URL of the Support Knowledge Base

# **v1_kb_articels_get**
> list[ArticleInfo] v1_kb_articels_get(search_text=search_text, limit=limit)

Get articles from the Support Knowledge Base

Get articles from VxRail Support Knowledge Base.

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
api_instance = swagger_client.SupportKnowledgeBaseApi(swagger_client.ApiClient(configuration))
search_text = '*' # str | An optional search term for narrowing the list of articles returned (optional) (default to *)
limit = 3 # int | The maximum number of articles that will be returned (optional) (default to 3)

try:
    # Get articles from the Support Knowledge Base
    api_response = api_instance.v1_kb_articels_get(search_text=search_text, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportKnowledgeBaseApi->v1_kb_articels_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_text** | **str**| An optional search term for narrowing the list of articles returned | [optional] [default to *]
 **limit** | **int**| The maximum number of articles that will be returned | [optional] [default to 3]

### Return type

[**list[ArticleInfo]**](ArticleInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_kb_get**
> KnowledgeBaseInfo v1_kb_get()

Get the URL of the Support Knowledge Base

Get the home URL of the VxRail Support Knowledge Base (KB).

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
api_instance = swagger_client.SupportKnowledgeBaseApi(swagger_client.ApiClient(configuration))

try:
    # Get the URL of the Support Knowledge Base
    api_response = api_instance.v1_kb_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportKnowledgeBaseApi->v1_kb_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**KnowledgeBaseInfo**](KnowledgeBaseInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

