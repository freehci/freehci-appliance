# swagger_client.HostIDRACConfigurationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_hosts_sn_idrac_id_get**](HostIDRACConfigurationApi.md#v1_hosts_sn_idrac_id_get) | **GET** /v1/hosts/{sn}/idrac/available-user-ids | Get a list of iDRAC user slot IDs
[**v1_hosts_sn_idrac_network_get**](HostIDRACConfigurationApi.md#v1_hosts_sn_idrac_network_get) | **GET** /v1/hosts/{sn}/idrac/network | Get the iDRAC network settings
[**v1_hosts_sn_idrac_network_patch**](HostIDRACConfigurationApi.md#v1_hosts_sn_idrac_network_patch) | **PATCH** /v1/hosts/{sn}/idrac/network | Update the iDRAC network settings
[**v1_hosts_sn_idrac_user_get**](HostIDRACConfigurationApi.md#v1_hosts_sn_idrac_user_get) | **GET** /v1/hosts/{sn}/idrac/users | Get a list of iDRAC user accounts
[**v1_hosts_sn_idrac_user_id_put**](HostIDRACConfigurationApi.md#v1_hosts_sn_idrac_user_id_put) | **PUT** /v1/hosts/{sn}/idrac/users/{userId} | Update an iDRAC user account
[**v1_hosts_sn_idrac_user_post**](HostIDRACConfigurationApi.md#v1_hosts_sn_idrac_user_post) | **POST** /v1/hosts/{sn}/idrac/users | Create an iDRAC user account
[**v2_hosts_sn_idrac_network_get**](HostIDRACConfigurationApi.md#v2_hosts_sn_idrac_network_get) | **GET** /v2/hosts/{sn}/idrac/network | Get the iDRAC network settings
[**v2_hosts_sn_idrac_network_patch**](HostIDRACConfigurationApi.md#v2_hosts_sn_idrac_network_patch) | **PATCH** /v2/hosts/{sn}/idrac/network | Update the iDRAC network settings

# **v1_hosts_sn_idrac_id_get**
> list[int] v1_hosts_sn_idrac_id_get(sn)

Get a list of iDRAC user slot IDs

Get a list of the available iDRAC user slot IDs.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the host to be queried.

try:
    # Get a list of iDRAC user slot IDs
    api_response = api_instance.v1_hosts_sn_idrac_id_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v1_hosts_sn_idrac_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the host to be queried. | 

### Return type

**list[int]**

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_idrac_network_get**
> IdracNetworkInfo v1_hosts_sn_idrac_network_get(sn)

Get the iDRAC network settings

Get the iDRAC network settings on the specified host.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the host to be queried.

try:
    # Get the iDRAC network settings
    api_response = api_instance.v1_hosts_sn_idrac_network_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v1_hosts_sn_idrac_network_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the host to be queried. | 

### Return type

[**IdracNetworkInfo**](IdracNetworkInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_idrac_network_patch**
> Model202Nocontent v1_hosts_sn_idrac_network_patch(body, sn)

Update the iDRAC network settings

Update the iDRAC network settings on the specified host.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
body = swagger_client.IdracNetworkSpec() # IdracNetworkSpec | The network parameters for the iDRAC network.
sn = 'sn_example' # str | The serial number of the host to be queried.

try:
    # Update the iDRAC network settings
    api_response = api_instance.v1_hosts_sn_idrac_network_patch(body, sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v1_hosts_sn_idrac_network_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**IdracNetworkSpec**](IdracNetworkSpec.md)| The network parameters for the iDRAC network. | 
 **sn** | **str**| The serial number of the host to be queried. | 

### Return type

[**Model202Nocontent**](Model202Nocontent.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_idrac_user_get**
> list[IdracUserInfo] v1_hosts_sn_idrac_user_get(sn)

Get a list of iDRAC user accounts

Get a list of the iDRAC user accounts on the specified host.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the host to be queried.

try:
    # Get a list of iDRAC user accounts
    api_response = api_instance.v1_hosts_sn_idrac_user_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v1_hosts_sn_idrac_user_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the host to be queried. | 

### Return type

[**list[IdracUserInfo]**](IdracUserInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_idrac_user_id_put**
> Model202Nocontent v1_hosts_sn_idrac_user_id_put(body, sn, user_id)

Update an iDRAC user account

Update an iDRAC user account.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
body = swagger_client.IdracUserUpdateSpec() # IdracUserUpdateSpec | The iDRAC user account information for the user to be updated.
sn = 'sn_example' # str | The serial number of the host to be queried.
user_id = 'user_id_example' # str | The unique identifier of the iDRAC user. The available range is between 3 and 16.

try:
    # Update an iDRAC user account
    api_response = api_instance.v1_hosts_sn_idrac_user_id_put(body, sn, user_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v1_hosts_sn_idrac_user_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**IdracUserUpdateSpec**](IdracUserUpdateSpec.md)| The iDRAC user account information for the user to be updated. | 
 **sn** | **str**| The serial number of the host to be queried. | 
 **user_id** | **str**| The unique identifier of the iDRAC user. The available range is between 3 and 16. | 

### Return type

[**Model202Nocontent**](Model202Nocontent.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_idrac_user_post**
> Model202Nocontent v1_hosts_sn_idrac_user_post(body, sn)

Create an iDRAC user account

Create an iDRAC user account.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
body = swagger_client.IdracUserCreateSpec() # IdracUserCreateSpec | The iDRAC user account information for the user to be created.
sn = 'sn_example' # str | The serial number of the host to be queried.

try:
    # Create an iDRAC user account
    api_response = api_instance.v1_hosts_sn_idrac_user_post(body, sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v1_hosts_sn_idrac_user_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**IdracUserCreateSpec**](IdracUserCreateSpec.md)| The iDRAC user account information for the user to be created. | 
 **sn** | **str**| The serial number of the host to be queried. | 

### Return type

[**Model202Nocontent**](Model202Nocontent.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_hosts_sn_idrac_network_get**
> IdracNetworkInfoWithIPv6 v2_hosts_sn_idrac_network_get(sn)

Get the iDRAC network settings

Get the iDRAC network settings on the specified host.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the host to be queried.

try:
    # Get the iDRAC network settings
    api_response = api_instance.v2_hosts_sn_idrac_network_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v2_hosts_sn_idrac_network_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the host to be queried. | 

### Return type

[**IdracNetworkInfoWithIPv6**](IdracNetworkInfoWithIPv6.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_hosts_sn_idrac_network_patch**
> Model202Nocontent v2_hosts_sn_idrac_network_patch(body, sn)

Update the iDRAC network settings

Update the iDRAC network settings on the specified host.

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
api_instance = swagger_client.HostIDRACConfigurationApi(swagger_client.ApiClient(configuration))
body = swagger_client.IdracNetworkIPv6Spec() # IdracNetworkIPv6Spec | The network parameters for the iDRAC network.
sn = 'sn_example' # str | The serial number of the host to be queried.

try:
    # Update the iDRAC network settings
    api_response = api_instance.v2_hosts_sn_idrac_network_patch(body, sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostIDRACConfigurationApi->v2_hosts_sn_idrac_network_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**IdracNetworkIPv6Spec**](IdracNetworkIPv6Spec.md)| The network parameters for the iDRAC network. | 
 **sn** | **str**| The serial number of the host to be queried. | 

### Return type

[**Model202Nocontent**](Model202Nocontent.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

