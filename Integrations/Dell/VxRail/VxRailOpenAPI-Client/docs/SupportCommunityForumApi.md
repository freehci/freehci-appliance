# swagger_client.SupportCommunityForumApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_support_community_get**](SupportCommunityForumApi.md#v1_support_community_get) | **GET** /v1/support/community | Get the home URL for accessing the VxRail community
[**v1_support_community_message_get**](SupportCommunityForumApi.md#v1_support_community_message_get) | **GET** /v1/support/community/messages | Get VxRail community messages

# **v1_support_community_get**
> CommunityInfo v1_support_community_get()

Get the home URL for accessing the VxRail community

Get the home URL for accessing the VxRail community.

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
api_instance = swagger_client.SupportCommunityForumApi(swagger_client.ApiClient(configuration))

try:
    # Get the home URL for accessing the VxRail community
    api_response = api_instance.v1_support_community_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportCommunityForumApi->v1_support_community_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**CommunityInfo**](CommunityInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_support_community_message_get**
> list[MessageInfo] v1_support_community_message_get(limit=limit)

Get VxRail community messages

Get VxRail community messages.

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
api_instance = swagger_client.SupportCommunityForumApi(swagger_client.ApiClient(configuration))
limit = 3 # int | The number of messages the user wants to receive (optional) (default to 3)

try:
    # Get VxRail community messages
    api_response = api_instance.v1_support_community_message_get(limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportCommunityForumApi->v1_support_community_message_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| The number of messages the user wants to receive | [optional] [default to 3]

### Return type

[**list[MessageInfo]**](MessageInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

