# swagger_client.HostInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v10_hosts_get**](HostInformationApi.md#v10_hosts_get) | **GET** /v10/hosts | Retrieves a list of VxRail hosts (v10).
[**v10_hosts_sn_get**](HostInformationApi.md#v10_hosts_sn_get) | **GET** /v10/hosts/{sn} | Get information about a host (v9).
[**v1_hosts_get**](HostInformationApi.md#v1_hosts_get) | **GET** /v1/hosts | Get a list of VxRail hosts (v1)
[**v1_hosts_sn_get**](HostInformationApi.md#v1_hosts_sn_get) | **GET** /v1/hosts/{sn} | Get information about a host (v1)
[**v1_hosts_sn_patch**](HostInformationApi.md#v1_hosts_sn_patch) | **PATCH** /v1/hosts/{sn} | Update the geographical information about a host
[**v1_hosts_sn_shutdown_post**](HostInformationApi.md#v1_hosts_sn_shutdown_post) | **POST** /v1/hosts/{sn}/shutdown | Shut down a host or perform a shutdown dry run
[**v2_hosts_get**](HostInformationApi.md#v2_hosts_get) | **GET** /v2/hosts | Get a list of VxRail hosts (v2)
[**v2_hosts_sn_get**](HostInformationApi.md#v2_hosts_sn_get) | **GET** /v2/hosts/{sn} | Get information about a host (v2)
[**v3_hosts_get**](HostInformationApi.md#v3_hosts_get) | **GET** /v3/hosts | Get a list of VxRail hosts (v3)
[**v3_hosts_sn_get**](HostInformationApi.md#v3_hosts_sn_get) | **GET** /v3/hosts/{sn} | Get information about a host (v3)
[**v4_hosts_get**](HostInformationApi.md#v4_hosts_get) | **GET** /v4/hosts | Get a list of VxRail hosts (v4)
[**v4_hosts_sn_get**](HostInformationApi.md#v4_hosts_sn_get) | **GET** /v4/hosts/{sn} | Get information about a host (v4)
[**v5_hosts_get**](HostInformationApi.md#v5_hosts_get) | **GET** /v5/hosts | Get a list of VxRail hosts (v5)
[**v5_hosts_sn_get**](HostInformationApi.md#v5_hosts_sn_get) | **GET** /v5/hosts/{sn} | Get information about a host (v5)
[**v6_hosts_get**](HostInformationApi.md#v6_hosts_get) | **GET** /v6/hosts | Get a list of VxRail hosts (v6)
[**v6_hosts_sn_get**](HostInformationApi.md#v6_hosts_sn_get) | **GET** /v6/hosts/{sn} | Get information about a host (v6)
[**v7_hosts_get**](HostInformationApi.md#v7_hosts_get) | **GET** /v7/hosts | Get a list of VxRail hosts (v7)
[**v7_hosts_sn_get**](HostInformationApi.md#v7_hosts_sn_get) | **GET** /v7/hosts/{sn} | Get information about a host (v7)
[**v8_hosts_get**](HostInformationApi.md#v8_hosts_get) | **GET** /v8/hosts | Get a list of VxRail hosts (v8).
[**v8_hosts_sn_get**](HostInformationApi.md#v8_hosts_sn_get) | **GET** /v8/hosts/{sn} | Get information about a host (v8).

# **v10_hosts_get**
> list[HostV10] v10_hosts_get()

Retrieves a list of VxRail hosts (v10).

New fields are added to v10 to distinguish between base storage and optional storage (vSphere 7.x only).

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Retrieves a list of VxRail hosts (v10).
    api_response = api_instance.v10_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v10_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV10]**](HostV10.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v10_hosts_sn_get**
> HostV10 v10_hosts_sn_get(sn)

Get information about a host (v9).

Version v9 adds new fields to distinguish between base storage and optional storage.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to retrieve information for.

try:
    # Get information about a host (v9).
    api_response = api_instance.v10_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v10_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to retrieve information for. | 

### Return type

[**HostV10**](HostV10.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_get**
> list[Host] v1_hosts_get()

Get a list of VxRail hosts (v1)

Get a list of VxRail hosts and their associated subcomponent information.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v1)
    api_response = api_instance.v1_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v1_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Host]**](Host.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_get**
> Host v1_hosts_sn_get(sn)

Get information about a host (v1)

Get information about a specific host and its associated subcomponents.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to access.

try:
    # Get information about a host (v1)
    api_response = api_instance.v1_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v1_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to access. | 

### Return type

[**Host**](Host.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_patch**
> InlineResponse202 v1_hosts_sn_patch(body, sn)

Update the geographical information about a host

Update the geographical information about a specific host.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
body = swagger_client.HostUpdateSpec() # HostUpdateSpec | Geographical information about the host that you want to update.
sn = 'sn_example' # str | The serial number of the node that you want to access.

try:
    # Update the geographical information about a host
    api_response = api_instance.v1_hosts_sn_patch(body, sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v1_hosts_sn_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HostUpdateSpec**](HostUpdateSpec.md)| Geographical information about the host that you want to update. | 
 **sn** | **str**| The serial number of the node that you want to access. | 

### Return type

[**InlineResponse202**](InlineResponse202.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_hosts_sn_shutdown_post**
> InlineResponse202 v1_hosts_sn_shutdown_post(body, sn)

Shut down a host or perform a shutdown dry run

Shut down a selected host or perform a shutdown dry run.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
body = swagger_client.HostShutdownSpec() # HostShutdownSpec | Information required to shutdown the host.
sn = 'sn_example' # str | The serial number of the node that you want to shut down.

try:
    # Shut down a host or perform a shutdown dry run
    api_response = api_instance.v1_hosts_sn_shutdown_post(body, sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v1_hosts_sn_shutdown_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HostShutdownSpec**](HostShutdownSpec.md)| Information required to shutdown the host. | 
 **sn** | **str**| The serial number of the node that you want to shut down. | 

### Return type

[**InlineResponse202**](InlineResponse202.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_hosts_get**
> list[HostV2] v2_hosts_get()

Get a list of VxRail hosts (v2)

Get a list of VxRail hosts and their subcomponent information. Version v2 contains the same attributes as the v1 version with the addition of a geo-location attribute in the HostV2 schema.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v2)
    api_response = api_instance.v2_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v2_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV2]**](HostV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_hosts_sn_get**
> HostV2 v2_hosts_sn_get(sn)

Get information about a host (v2)

Get information about a specific host and its associated subcomponents. Version v2 contains the same attributes as the v1 version with the addition of a geo-location attribute in the HostV2 schema.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to update.

try:
    # Get information about a host (v2)
    api_response = api_instance.v2_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v2_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to update. | 

### Return type

[**HostV2**](HostV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v3_hosts_get**
> list[HostV3] v3_hosts_get()

Get a list of VxRail hosts (v3)

Get a list of VxRail hosts and their associated subcomponent information. Version v3 contains the same attributes as the v2 version with the addition of a dcpm_version attribute in FirmwareInfoV2 and a disk_claim_type attribute in DiskInfoV2.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v3)
    api_response = api_instance.v3_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v3_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV3]**](HostV3.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v3_hosts_sn_get**
> HostV3 v3_hosts_sn_get(sn)

Get information about a host (v3)

Get information about a specific host and its associated subcomponents. Version v3 contains the same attributes as the v2 version with the addition of a dcpm_version attribute in FirmwareInfoV2 and a disk_claim_type attribute in DiskInfoV2.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to update.

try:
    # Get information about a host (v3)
    api_response = api_instance.v3_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v3_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to update. | 

### Return type

[**HostV3**](HostV3.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v4_hosts_get**
> list[HostV4] v4_hosts_get()

Get a list of VxRail hosts (v4)

Get a list of VxRail hosts and their associated subcomponent information. Version v4 contains drive configuration and BOSS card information.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v4)
    api_response = api_instance.v4_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v4_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV4]**](HostV4.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v4_hosts_sn_get**
> HostV4 v4_hosts_sn_get(sn)

Get information about a host (v4)

Get information about a specific host and its associated subcomponents. Version v4 contains drive configuration and BOSS card information.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to update.

try:
    # Get information about a host (v4)
    api_response = api_instance.v4_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v4_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to update. | 

### Return type

[**HostV4**](HostV4.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v5_hosts_get**
> list[HostV5] v5_hosts_get()

Get a list of VxRail hosts (v5)

Get a list of VxRail hosts and their associated subcomponent information. Version v5 provides support for satellite nodes, adding a new field 'type'.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v5)
    api_response = api_instance.v5_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v5_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV5]**](HostV5.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v5_hosts_sn_get**
> HostV5 v5_hosts_sn_get(sn)

Get information about a host (v5)

Get information about a specific host and its associated subcomponents. Version v5 provides support for satellite nodes, adding a new field 'type'.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to update.

try:
    # Get information about a host (v5)
    api_response = api_instance.v5_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v5_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to update. | 

### Return type

[**HostV5**](HostV5.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v6_hosts_get**
> list[HostV6] v6_hosts_get()

Get a list of VxRail hosts (v6)

Version v6 contains new nic version, which contains type, port and drivers field.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v6)
    api_response = api_instance.v6_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v6_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV6]**](HostV6.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v6_hosts_sn_get**
> HostV6 v6_hosts_sn_get(sn)

Get information about a host (v6)

Version v6 contains new nic version, which contains type, port and drivers field.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to update.

try:
    # Get information about a host (v6)
    api_response = api_instance.v6_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v6_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to update. | 

### Return type

[**HostV6**](HostV6.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v7_hosts_get**
> list[HostV7] v7_hosts_get()

Get a list of VxRail hosts (v7)

Version v7 adds the new fields to support encryption.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v7)
    api_response = api_instance.v7_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v7_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV7]**](HostV7.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v7_hosts_sn_get**
> HostV7 v7_hosts_sn_get(sn)

Get information about a host (v7)

Version v7 contains new fields to support encryption.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to retrieve inforamtion for.

try:
    # Get information about a host (v7)
    api_response = api_instance.v7_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v7_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to retrieve inforamtion for. | 

### Return type

[**HostV7**](HostV7.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v8_hosts_get**
> list[HostV8] v8_hosts_get()

Get a list of VxRail hosts (v8).

Version v8 adds the new fields to get WWNN/WWPN of Fibre Channel cards.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail hosts (v8).
    api_response = api_instance.v8_hosts_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v8_hosts_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HostV8]**](HostV8.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v8_hosts_sn_get**
> HostV8 v8_hosts_sn_get(sn)

Get information about a host (v8).

Version v8 adds the new fields to get WWNN/WWPN of Fibre Channel cards.

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
api_instance = swagger_client.HostInformationApi(swagger_client.ApiClient(configuration))
sn = 'sn_example' # str | The serial number of the node that you want to retrieve inforamtion for.

try:
    # Get information about a host (v8).
    api_response = api_instance.v8_hosts_sn_get(sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HostInformationApi->v8_hosts_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sn** | **str**| The serial number of the node that you want to retrieve inforamtion for. | 

### Return type

[**HostV8**](HostV8.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

