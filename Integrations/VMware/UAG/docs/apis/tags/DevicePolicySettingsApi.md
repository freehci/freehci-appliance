<a name="__pageTop"></a>
# openapi_client.apis.tags.device_policy_settings_api.DevicePolicySettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_device_policy**](#add_device_policy) | **put** /v1/config/devicepolicy | Add or update OPSWAT device policy check service provider.
[**add_opswat_device_policy**](#add_opswat_device_policy) | **put** /v1/config/devicepolicy/opswat | Add or update OPSWAT device policy check service provider.
[**add_ws1_risk_score_device_policy**](#add_ws1_risk_score_device_policy) | **put** /v1/config/devicepolicy/ws1IntelligenceRiskScore | Add or update Workspace ONE Intelligence Risk Score device policy check service provider.
[**delete_device_policy_settings**](#delete_device_policy_settings) | **delete** /v1/config/devicepolicy/{name} | Delete a device policy check service provider.
[**get_all_configured_device_policy_providers**](#get_all_configured_device_policy_providers) | **get** /v1/config/devicepolicy/available | Get all device policy service providers to be configured.
[**get_all_device_policy_providers_configured**](#get_all_device_policy_providers_configured) | **get** /v1/config/devicepolicy/configured | Get all configured device policy check service providers.
[**get_device_policy_settings**](#get_device_policy_settings) | **get** /v1/config/devicepolicy/{name} | Get all device policies configured.

# **add_device_policy**
<a name="add_device_policy"></a>
> OpswatDevicePolicySettings add_device_policy()

Add or update OPSWAT device policy check service provider.

### Example

```python
import openapi_client
from openapi_client.apis.tags import device_policy_settings_api
from openapi_client.model.opswat_device_policy_settings import OpswatDevicePolicySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = device_policy_settings_api.DevicePolicySettingsApi(api_client)

    # example passing only optional values
    body = OpswatDevicePolicySettings(None)
    try:
        # Add or update OPSWAT device policy check service provider.
        api_response = api_instance.add_device_policy(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DevicePolicySettingsApi->add_device_policy: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OpswatDevicePolicySettings**](../../models/OpswatDevicePolicySettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#add_device_policy.ApiResponseFor200) | successful operation

#### add_device_policy.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OpswatDevicePolicySettings**](../../models/OpswatDevicePolicySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **add_opswat_device_policy**
<a name="add_opswat_device_policy"></a>
> OpswatDevicePolicySettings add_opswat_device_policy()

Add or update OPSWAT device policy check service provider.

### Example

```python
import openapi_client
from openapi_client.apis.tags import device_policy_settings_api
from openapi_client.model.opswat_device_policy_settings import OpswatDevicePolicySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = device_policy_settings_api.DevicePolicySettingsApi(api_client)

    # example passing only optional values
    body = OpswatDevicePolicySettings(None)
    try:
        # Add or update OPSWAT device policy check service provider.
        api_response = api_instance.add_opswat_device_policy(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DevicePolicySettingsApi->add_opswat_device_policy: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OpswatDevicePolicySettings**](../../models/OpswatDevicePolicySettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#add_opswat_device_policy.ApiResponseFor200) | successful operation

#### add_opswat_device_policy.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OpswatDevicePolicySettings**](../../models/OpswatDevicePolicySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **add_ws1_risk_score_device_policy**
<a name="add_ws1_risk_score_device_policy"></a>
> WorkspaceOneIntelligenceRiskScoreSettings add_ws1_risk_score_device_policy()

Add or update Workspace ONE Intelligence Risk Score device policy check service provider.

### Example

```python
import openapi_client
from openapi_client.apis.tags import device_policy_settings_api
from openapi_client.model.workspace_one_intelligence_risk_score_settings import WorkspaceOneIntelligenceRiskScoreSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = device_policy_settings_api.DevicePolicySettingsApi(api_client)

    # example passing only optional values
    body = WorkspaceOneIntelligenceRiskScoreSettings(None)
    try:
        # Add or update Workspace ONE Intelligence Risk Score device policy check service provider.
        api_response = api_instance.add_ws1_risk_score_device_policy(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DevicePolicySettingsApi->add_ws1_risk_score_device_policy: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**WorkspaceOneIntelligenceRiskScoreSettings**](../../models/WorkspaceOneIntelligenceRiskScoreSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#add_ws1_risk_score_device_policy.ApiResponseFor200) | successful operation

#### add_ws1_risk_score_device_policy.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**WorkspaceOneIntelligenceRiskScoreSettings**](../../models/WorkspaceOneIntelligenceRiskScoreSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_device_policy_settings**
<a name="delete_device_policy_settings"></a>
> DevicePolicySettings delete_device_policy_settings(name)

Delete a device policy check service provider.

Delete a configured device policy check service provider.

### Example

```python
import openapi_client
from openapi_client.apis.tags import device_policy_settings_api
from openapi_client.model.device_policy_settings import DevicePolicySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = device_policy_settings_api.DevicePolicySettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Delete a device policy check service provider.
        api_response = api_instance.delete_device_policy_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DevicePolicySettingsApi->delete_device_policy_settings: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
name | NameSchema | | 

# NameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#delete_device_policy_settings.ApiResponseFor200) | successful operation

#### delete_device_policy_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**DevicePolicySettings**](../../models/DevicePolicySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_configured_device_policy_providers**
<a name="get_all_configured_device_policy_providers"></a>
> DevicePolicySettings get_all_configured_device_policy_providers()

Get all device policy service providers to be configured.

Get all device policy service providers to be configured.

### Example

```python
import openapi_client
from openapi_client.apis.tags import device_policy_settings_api
from openapi_client.model.device_policy_settings import DevicePolicySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = device_policy_settings_api.DevicePolicySettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all device policy service providers to be configured.
        api_response = api_instance.get_all_configured_device_policy_providers()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DevicePolicySettingsApi->get_all_configured_device_policy_providers: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_configured_device_policy_providers.ApiResponseFor200) | successful operation

#### get_all_configured_device_policy_providers.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**DevicePolicySettings**](../../models/DevicePolicySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_device_policy_providers_configured**
<a name="get_all_device_policy_providers_configured"></a>
> DevicePolicySettingsList get_all_device_policy_providers_configured()

Get all configured device policy check service providers.

### Example

```python
import openapi_client
from openapi_client.apis.tags import device_policy_settings_api
from openapi_client.model.device_policy_settings_list import DevicePolicySettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = device_policy_settings_api.DevicePolicySettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all configured device policy check service providers.
        api_response = api_instance.get_all_device_policy_providers_configured()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DevicePolicySettingsApi->get_all_device_policy_providers_configured: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_device_policy_providers_configured.ApiResponseFor200) | successful operation

#### get_all_device_policy_providers_configured.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**DevicePolicySettingsList**](../../models/DevicePolicySettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_device_policy_settings**
<a name="get_device_policy_settings"></a>
> DevicePolicySettings get_device_policy_settings(name)

Get all device policies configured.

Get all device policies service providers configured.

### Example

```python
import openapi_client
from openapi_client.apis.tags import device_policy_settings_api
from openapi_client.model.device_policy_settings import DevicePolicySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = device_policy_settings_api.DevicePolicySettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Get all device policies configured.
        api_response = api_instance.get_device_policy_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling DevicePolicySettingsApi->get_device_policy_settings: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
name | NameSchema | | 

# NameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_device_policy_settings.ApiResponseFor200) | successful operation

#### get_device_policy_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**DevicePolicySettings**](../../models/DevicePolicySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

