# swagger_client.CallHomeOperationsApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**callhome_info_get_v1**](CallHomeOperationsApi.md#callhome_info_get_v1) | **GET** /v1/callhome/info | Get call home server information (v1)
[**v1_callhome_access_code_post**](CallHomeOperationsApi.md#v1_callhome_access_code_post) | **POST** /v1/callhome/access-code | Generate access code to activate internal call home server
[**v1_callhome_deployment_post**](CallHomeOperationsApi.md#v1_callhome_deployment_post) | **POST** /v1/callhome/deployment | Deploy internal call home server (v1)
[**v1_callhome_disable_delete**](CallHomeOperationsApi.md#v1_callhome_disable_delete) | **DELETE** /v1/callhome/disable | Unregister call home servers
[**v1_callhome_enable_post**](CallHomeOperationsApi.md#v1_callhome_enable_post) | **POST** /v1/callhome/enable | Enable call home functionality
[**v1_callhome_external_register_post**](CallHomeOperationsApi.md#v1_callhome_external_register_post) | **POST** /v1/callhome/external/register | Register external call home servers (v1)
[**v1_callhome_internal_register_post**](CallHomeOperationsApi.md#v1_callhome_internal_register_post) | **POST** /v1/callhome/internal/register | Activate and register internal call home server
[**v1_callhome_internal_upgrade_post**](CallHomeOperationsApi.md#v1_callhome_internal_upgrade_post) | **POST** /v1/callhome/internal/upgrade | Upgrade internal SRS software
[**v2_callhome_deployment_post**](CallHomeOperationsApi.md#v2_callhome_deployment_post) | **POST** /v2/callhome/deployment | Deploy internal call home server (v2)
[**v2_callhome_external_register_post**](CallHomeOperationsApi.md#v2_callhome_external_register_post) | **POST** /v2/callhome/external/register | Register external call home servers (v2)
[**v2_callhome_info**](CallHomeOperationsApi.md#v2_callhome_info) | **GET** /v2/callhome/info | Get call home server information (v2)

# **callhome_info_get_v1**
> CallhomeInfo callhome_info_get_v1()

Get call home server information (v1)

Retrieve information about the call home servers. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))

try:
    # Get call home server information (v1)
    api_response = api_instance.callhome_info_get_v1()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->callhome_info_get_v1: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**CallhomeInfo**](CallhomeInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_callhome_access_code_post**
> Componentsresponses200 v1_callhome_access_code_post()

Generate access code to activate internal call home server

Generate an access code to activate the internal call home server. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))

try:
    # Generate access code to activate internal call home server
    api_response = api_instance.v1_callhome_access_code_post()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v1_callhome_access_code_post: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_callhome_deployment_post**
> Componentsresponses200 v1_callhome_deployment_post(body)

Deploy internal call home server (v1)

Deploy an internal call home server. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))
body = swagger_client.CallhomeDeploySpec() # CallhomeDeploySpec | Information about the SRS server to be deployed.

try:
    # Deploy internal call home server (v1)
    api_response = api_instance.v1_callhome_deployment_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v1_callhome_deployment_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CallhomeDeploySpec**](CallhomeDeploySpec.md)| Information about the SRS server to be deployed. | 

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_callhome_disable_delete**
> v1_callhome_disable_delete()

Unregister call home servers

Unregister call home servers and delete the SRS VE virtual machine if it exists.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))

try:
    # Unregister call home servers
    api_instance.v1_callhome_disable_delete()
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v1_callhome_disable_delete: %s\n" % e)
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

# **v1_callhome_enable_post**
> v1_callhome_enable_post(body)

Enable call home functionality

Enable call home functionality by enabing remote connectivity service.<br/> if remote connector type is ESE <br/>     1) update ESE state to configuring <br/>     2) Initialize ESE lockbox<br/>     3) Update ESE configuation (product/gateway/proxy )<br/>     4) Generate universal key by PIN/access key or upload pre-installed universal key to ESE <br/>     5) Enable ESE connection<br/>     6) update ESE state to configured<br/>

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))
body = swagger_client.EnableCallhomeSpec() # EnableCallhomeSpec | 

try:
    # Enable call home functionality
    api_instance.v1_callhome_enable_post(body)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v1_callhome_enable_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**EnableCallhomeSpec**](EnableCallhomeSpec.md)|  | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_callhome_external_register_post**
> Componentsresponses200 v1_callhome_external_register_post(body)

Register external call home servers (v1)

Register external call home servers. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))
body = swagger_client.ExternalCallhomeRegisterSpec() # ExternalCallhomeRegisterSpec | Information about each of the external SRS servers to be registered.

try:
    # Register external call home servers (v1)
    api_response = api_instance.v1_callhome_external_register_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v1_callhome_external_register_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ExternalCallhomeRegisterSpec**](ExternalCallhomeRegisterSpec.md)| Information about each of the external SRS servers to be registered. | 

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_callhome_internal_register_post**
> Componentsresponses200 v1_callhome_internal_register_post(body)

Activate and register internal call home server

Activate and register an internal call home server. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))
body = swagger_client.AccessCodeSpec() # AccessCodeSpec | Access code for activating an internal call home server.

try:
    # Activate and register internal call home server
    api_response = api_instance.v1_callhome_internal_register_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v1_callhome_internal_register_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AccessCodeSpec**](AccessCodeSpec.md)| Access code for activating an internal call home server. | 

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_callhome_internal_upgrade_post**
> Componentsresponses200 v1_callhome_internal_upgrade_post(body)

Upgrade internal SRS software

Upgrade the internal SRS software. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))
body = swagger_client.SRSUpgradeSpec() # SRSUpgradeSpec | Parameters for activating a software upgrade on the internal SRS server.

try:
    # Upgrade internal SRS software
    api_response = api_instance.v1_callhome_internal_upgrade_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v1_callhome_internal_upgrade_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SRSUpgradeSpec**](SRSUpgradeSpec.md)| Parameters for activating a software upgrade on the internal SRS server. | 

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_callhome_deployment_post**
> Componentsresponses200 v2_callhome_deployment_post(body)

Deploy internal call home server (v2)

Deploy an internal call home server. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))
body = swagger_client.CallhomeDeploySpecV2() # CallhomeDeploySpecV2 | Details for SRS to be deployed.

try:
    # Deploy internal call home server (v2)
    api_response = api_instance.v2_callhome_deployment_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v2_callhome_deployment_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CallhomeDeploySpecV2**](CallhomeDeploySpecV2.md)| Details for SRS to be deployed. | 

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_callhome_external_register_post**
> Componentsresponses200 v2_callhome_external_register_post(body)

Register external call home servers (v2)

Register external call home servers. This API has been deprecated and only response with status code 410 will be returned.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))
body = swagger_client.ExternalCallhomeRegisterSpecV2() # ExternalCallhomeRegisterSpecV2 | Information about each of the external SRS servers to be registered.

try:
    # Register external call home servers (v2)
    api_response = api_instance.v2_callhome_external_register_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v2_callhome_external_register_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ExternalCallhomeRegisterSpecV2**](ExternalCallhomeRegisterSpecV2.md)| Information about each of the external SRS servers to be registered. | 

### Return type

[**Componentsresponses200**](Componentsresponses200.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_callhome_info**
> CallhomeInfoV2 v2_callhome_info()

Get call home server information (v2)

Retrieve information about the call home servers.

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
api_instance = swagger_client.CallHomeOperationsApi(swagger_client.ApiClient(configuration))

try:
    # Get call home server information (v2)
    api_response = api_instance.v2_callhome_info()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CallHomeOperationsApi->v2_callhome_info: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**CallhomeInfoV2**](CallhomeInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

