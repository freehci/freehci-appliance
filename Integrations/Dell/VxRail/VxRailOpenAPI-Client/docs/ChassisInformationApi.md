# swagger_client.ChassisInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_chassis_get**](ChassisInformationApi.md#v1_chassis_get) | **GET** /v1/chassis | Get a list of VxRail chassis (v1)
[**v1_chassis_id_get**](ChassisInformationApi.md#v1_chassis_id_get) | **GET** /v1/chassis/{chassis_id} | Get information about a user-specified chassis (v1)
[**v2_chassis_get**](ChassisInformationApi.md#v2_chassis_get) | **GET** /v2/chassis | Get a list of VxRail chassis (v2)
[**v2_chassis_id_get**](ChassisInformationApi.md#v2_chassis_id_get) | **GET** /v2/chassis/{chassis_id} | Get information about a user-specified chassis (v2)
[**v3_chassis_get**](ChassisInformationApi.md#v3_chassis_get) | **GET** /v3/chassis | Get a list of VxRail chassis (v3)
[**v3_chassis_id_get**](ChassisInformationApi.md#v3_chassis_id_get) | **GET** /v3/chassis/{chassis_id} | Get information about a user-specified chassis (v3)
[**v4_chassis_get**](ChassisInformationApi.md#v4_chassis_get) | **GET** /v4/chassis | Get a list of VxRail chassis (v4)
[**v4_chassis_id_get**](ChassisInformationApi.md#v4_chassis_id_get) | **GET** /v4/chassis/{chassis_id} | Get information about a user-specified chassis (v4)
[**v5_chassis_get**](ChassisInformationApi.md#v5_chassis_get) | **GET** /v5/chassis | Get a list of VxRail chassis (v5)
[**v5_chassis_id_get**](ChassisInformationApi.md#v5_chassis_id_get) | **GET** /v5/chassis/{chassis_id} | Retrieves information about a user-specified chassis (v5)

# **v1_chassis_get**
> list[ChassisInfo] v1_chassis_get()

Get a list of VxRail chassis (v1)

Retrieve a list of VxRail chassis and information about the nodes in each chassis.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail chassis (v1)
    api_response = api_instance.v1_chassis_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v1_chassis_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ChassisInfo]**](ChassisInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_chassis_id_get**
> ChassisInfo v1_chassis_id_get(chassis_id)

Get information about a user-specified chassis (v1)

Get information about a user-specified VxRail chassis.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))
chassis_id = 'chassis_id_example' # str | The chassis ID for the VxRail chassis you want to query.

try:
    # Get information about a user-specified chassis (v1)
    api_response = api_instance.v1_chassis_id_get(chassis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v1_chassis_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chassis_id** | **str**| The chassis ID for the VxRail chassis you want to query. | 

### Return type

[**ChassisInfo**](ChassisInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_chassis_get**
> list[ChassisInfoV2] v2_chassis_get()

Get a list of VxRail chassis (v2)

Retrieve a list of VxRail chassis and information about the nodes in each chassis. Version v2 contains the same attributes as the v1 version plus a geo-location attribute in HostBasicInfoV2.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail chassis (v2)
    api_response = api_instance.v2_chassis_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v2_chassis_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ChassisInfoV2]**](ChassisInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_chassis_id_get**
> ChassisInfoV2 v2_chassis_id_get(chassis_id)

Get information about a user-specified chassis (v2)

Get information about the user-specified VxRail chassis. Version v2 contains the same attributes as the v1 version plus a geo-location attribute in HostBasicInfoV2.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))
chassis_id = 'chassis_id_example' # str | The chassis ID for the VxRail chassis you want to query.

try:
    # Get information about a user-specified chassis (v2)
    api_response = api_instance.v2_chassis_id_get(chassis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v2_chassis_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chassis_id** | **str**| The chassis ID for the VxRail chassis you want to query. | 

### Return type

[**ChassisInfoV2**](ChassisInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v3_chassis_get**
> list[ChassisInfoV3] v3_chassis_get()

Get a list of VxRail chassis (v3)

Retrieve a list of VxRail chassis and information about the nodes in each chassis.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail chassis (v3)
    api_response = api_instance.v3_chassis_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v3_chassis_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ChassisInfoV3]**](ChassisInfoV3.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v3_chassis_id_get**
> ChassisInfoV3 v3_chassis_id_get(chassis_id)

Get information about a user-specified chassis (v3)

Get information about the user-specified VxRail chassis.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))
chassis_id = 'chassis_id_example' # str | Chassis ID

try:
    # Get information about a user-specified chassis (v3)
    api_response = api_instance.v3_chassis_id_get(chassis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v3_chassis_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chassis_id** | **str**| Chassis ID | 

### Return type

[**ChassisInfoV3**](ChassisInfoV3.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v4_chassis_get**
> list[ChassisInfoV4] v4_chassis_get()

Get a list of VxRail chassis (v4)

Retrieve a list of VxRail chassis and information about the nodes in each chassis. The v4 version adds support for satellite nodes.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail chassis (v4)
    api_response = api_instance.v4_chassis_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v4_chassis_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ChassisInfoV4]**](ChassisInfoV4.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v4_chassis_id_get**
> ChassisInfoV4 v4_chassis_id_get(chassis_id)

Get information about a user-specified chassis (v4)

Get information about the user-specified VxRail chassis. The v4 version adds support for satellite nodes.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))
chassis_id = 'chassis_id_example' # str | Chassis ID

try:
    # Get information about a user-specified chassis (v4)
    api_response = api_instance.v4_chassis_id_get(chassis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v4_chassis_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chassis_id** | **str**| Chassis ID | 

### Return type

[**ChassisInfoV4**](ChassisInfoV4.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v5_chassis_get**
> list[ChassisInfoV5] v5_chassis_get()

Get a list of VxRail chassis (v5)

Retrieve a list of VxRail chassis and information about the nodes in each chassis. The v5 version adds support for the witness node.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of VxRail chassis (v5)
    api_response = api_instance.v5_chassis_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v5_chassis_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ChassisInfoV5]**](ChassisInfoV5.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v5_chassis_id_get**
> ChassisInfoV5 v5_chassis_id_get(chassis_id)

Retrieves information about a user-specified chassis (v5)

Retrieves information about the user-specified VxRail chassis. The v5 version adds support for satellite nodes.

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
api_instance = swagger_client.ChassisInformationApi(swagger_client.ApiClient(configuration))
chassis_id = 'chassis_id_example' # str | Chassis ID

try:
    # Retrieves information about a user-specified chassis (v5)
    api_response = api_instance.v5_chassis_id_get(chassis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ChassisInformationApi->v5_chassis_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chassis_id** | **str**| Chassis ID | 

### Return type

[**ChassisInfoV5**](ChassisInfoV5.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

