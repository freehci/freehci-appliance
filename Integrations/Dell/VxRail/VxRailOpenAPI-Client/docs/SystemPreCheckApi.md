# swagger_client.SystemPreCheckApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_system_precheck_post**](SystemPreCheckApi.md#v1_system_precheck_post) | **POST** /v1/system/precheck | Perform a pre-check
[**v1_system_precheck_results_get**](SystemPreCheckApi.md#v1_system_precheck_results_get) | **GET** /v1/system/prechecks/results | Get all pre-check reports
[**v1_system_precheck_results_id_get**](SystemPreCheckApi.md#v1_system_precheck_results_id_get) | **GET** /v1/system/prechecks/{id}/result | Get a pre-check result
[**v1_system_prechecks_profiles_get**](SystemPreCheckApi.md#v1_system_prechecks_profiles_get) | **GET** /v1/system/prechecks/profiles | List pre-check profiles
[**v1_system_prechecks_version_get**](SystemPreCheckApi.md#v1_system_prechecks_version_get) | **GET** /v1/system/prechecks/precheck-service-version | Get the pre-check version

# **v1_system_precheck_post**
> AsyncPrecheckSuccessResponse v1_system_precheck_post(body)

Perform a pre-check

Perform a system pre-check.

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
api_instance = swagger_client.SystemPreCheckApi(swagger_client.ApiClient(configuration))
body = swagger_client.PrecheckSpec() # PrecheckSpec | 

try:
    # Perform a pre-check
    api_response = api_instance.v1_system_precheck_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemPreCheckApi->v1_system_precheck_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PrecheckSpec**](PrecheckSpec.md)|  | 

### Return type

[**AsyncPrecheckSuccessResponse**](AsyncPrecheckSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_precheck_results_get**
> PrecheckReportsInfo v1_system_precheck_results_get()

Get all pre-check reports

Get a list of pre-check reports, which include the current running status and historical results.

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
api_instance = swagger_client.SystemPreCheckApi(swagger_client.ApiClient(configuration))

try:
    # Get all pre-check reports
    api_response = api_instance.v1_system_precheck_results_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemPreCheckApi->v1_system_precheck_results_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**PrecheckReportsInfo**](PrecheckReportsInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_precheck_results_id_get**
> PrecheckReport v1_system_precheck_results_id_get(id, verbose=verbose)

Get a pre-check result

Get a pre-check result using a specified request ID. Available reports include a status report from a currently running pre-check process or a report from previously run pre-check.

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
api_instance = swagger_client.SystemPreCheckApi(swagger_client.ApiClient(configuration))
id = 'id_example' # str | Request ID of the pre-check status that you want to query
verbose = true # bool | Whether to return a full or simplified report. The default is true. Set to true to return a full pre -check result report. Set to falsefor a simplified report. (optional)

try:
    # Get a pre-check result
    api_response = api_instance.v1_system_precheck_results_id_get(id, verbose=verbose)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemPreCheckApi->v1_system_precheck_results_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Request ID of the pre-check status that you want to query | 
 **verbose** | **bool**| Whether to return a full or simplified report. The default is true. Set to true to return a full pre -check result report. Set to falsefor a simplified report. | [optional] 

### Return type

[**PrecheckReport**](PrecheckReport.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_prechecks_profiles_get**
> list[ProfileInfo] v1_system_prechecks_profiles_get()

List pre-check profiles

Get a list of available pre-check profiles. Each profile represents a different type of pre-check that you can perform.

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
api_instance = swagger_client.SystemPreCheckApi(swagger_client.ApiClient(configuration))

try:
    # List pre-check profiles
    api_response = api_instance.v1_system_prechecks_profiles_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemPreCheckApi->v1_system_prechecks_profiles_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ProfileInfo]**](ProfileInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_prechecks_version_get**
> PrecheckVersion v1_system_prechecks_version_get()

Get the pre-check version

Get the current version of the pre-check service in the VxRail system.

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
api_instance = swagger_client.SystemPreCheckApi(swagger_client.ApiClient(configuration))

try:
    # Get the pre-check version
    api_response = api_instance.v1_system_prechecks_version_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemPreCheckApi->v1_system_prechecks_version_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**PrecheckVersion**](PrecheckVersion.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

