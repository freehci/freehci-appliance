# swagger_client.SupportAccountApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_support_account_delete**](SupportAccountApi.md#v1_support_account_delete) | **DELETE** /v1/support/account | Remove the support account
[**v1_support_account_get**](SupportAccountApi.md#v1_support_account_get) | **GET** /v1/support/account | Get the support account
[**v1_support_account_post**](SupportAccountApi.md#v1_support_account_post) | **POST** /v1/support/account | Add a support account
[**v1_support_account_put**](SupportAccountApi.md#v1_support_account_put) | **PUT** /v1/support/account | Update the support account

# **v1_support_account_delete**
> v1_support_account_delete()

Remove the support account

Remove the support account in VxRail Manager.

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
api_instance = swagger_client.SupportAccountApi(swagger_client.ApiClient(configuration))

try:
    # Remove the support account
    api_instance.v1_support_account_delete()
except ApiException as e:
    print("Exception when calling SupportAccountApi->v1_support_account_delete: %s\n" % e)
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

# **v1_support_account_get**
> SupportAccountInfo v1_support_account_get()

Get the support account

Get the current support account set in VxRail.

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
api_instance = swagger_client.SupportAccountApi(swagger_client.ApiClient(configuration))

try:
    # Get the support account
    api_response = api_instance.v1_support_account_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SupportAccountApi->v1_support_account_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**SupportAccountInfo**](SupportAccountInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_support_account_post**
> v1_support_account_post(body)

Add a support account

Add a support account to VxRail Manager.

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
api_instance = swagger_client.SupportAccountApi(swagger_client.ApiClient(configuration))
body = swagger_client.SupportAccountSpec() # SupportAccountSpec | The username and password of the support account.

try:
    # Add a support account
    api_instance.v1_support_account_post(body)
except ApiException as e:
    print("Exception when calling SupportAccountApi->v1_support_account_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SupportAccountSpec**](SupportAccountSpec.md)| The username and password of the support account. | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_support_account_put**
> v1_support_account_put(body)

Update the support account

Update the support account in VxRail Manager.

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
api_instance = swagger_client.SupportAccountApi(swagger_client.ApiClient(configuration))
body = swagger_client.SupportAccountSpec() # SupportAccountSpec | The username and password of the support account.

try:
    # Update the support account
    api_instance.v1_support_account_put(body)
except ApiException as e:
    print("Exception when calling SupportAccountApi->v1_support_account_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SupportAccountSpec**](SupportAccountSpec.md)| The username and password of the support account. | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

