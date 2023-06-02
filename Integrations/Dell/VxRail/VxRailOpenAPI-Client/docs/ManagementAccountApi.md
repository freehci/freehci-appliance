# swagger_client.ManagementAccountApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_system_accounts_management_get**](ManagementAccountApi.md#v1_system_accounts_management_get) | **GET** /v1/system/accounts/management | Get VC management account and ESXi host management accounts

# **v1_system_accounts_management_get**
> list[ManagementAccountV1] v1_system_accounts_management_get(component=component, hostname=hostname)

Get VC management account and ESXi host management accounts

Synchronize API to get VC management account and ESXi host management accounts.

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
api_instance = swagger_client.ManagementAccountApi(swagger_client.ApiClient(configuration))
component = 'component_example' # str | Component type can be \"ESXI\" or \"VC\". (optional)
hostname = 'hostname_example' # str | ESXi host name. If the ESXi host name is not provided, then the hosts for all accounts will be returned. (optional)

try:
    # Get VC management account and ESXi host management accounts
    api_response = api_instance.v1_system_accounts_management_get(component=component, hostname=hostname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ManagementAccountApi->v1_system_accounts_management_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **component** | **str**| Component type can be \&quot;ESXI\&quot; or \&quot;VC\&quot;. | [optional] 
 **hostname** | **str**| ESXi host name. If the ESXi host name is not provided, then the hosts for all accounts will be returned. | [optional] 

### Return type

[**list[ManagementAccountV1]**](ManagementAccountV1.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

