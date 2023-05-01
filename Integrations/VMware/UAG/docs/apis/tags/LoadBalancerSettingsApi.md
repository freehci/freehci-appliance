<a name="__pageTop"></a>
# openapi_client.apis.tags.load_balancer_settings_api.LoadBalancerSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_update_load_balancer_settings**](#add_update_load_balancer_settings) | **put** /v1/config/loadbalancer/settings | Add/Update Load balancer settings
[**get_ha_stats**](#get_ha_stats) | **get** /v1/config/loadbalancer/stats | Get HA stats
[**get_load_balancer_settings**](#get_load_balancer_settings) | **get** /v1/config/loadbalancer/settings | Get Load balancer settings
[**get_load_balancer_state**](#get_load_balancer_state) | **get** /v1/config/loadbalancer/state | Get Load balancer state

# **add_update_load_balancer_settings**
<a name="add_update_load_balancer_settings"></a>
> LoadBalancerSettings add_update_load_balancer_settings()

Add/Update Load balancer settings

Provide virtual IP address and Load balancer group ID

### Example

```python
import openapi_client
from openapi_client.apis.tags import load_balancer_settings_api
from openapi_client.model.load_balancer_settings import LoadBalancerSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = load_balancer_settings_api.LoadBalancerSettingsApi(api_client)

    # example passing only optional values
    body = LoadBalancerSettings(
        virtual_ip_address="virtual_ip_address_example",
        group_id=1,
        load_balancer_mode="DISABLED",
    )
    try:
        # Add/Update Load balancer settings
        api_response = api_instance.add_update_load_balancer_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LoadBalancerSettingsApi->add_update_load_balancer_settings: %s\n" % e)
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
[**LoadBalancerSettings**](../../models/LoadBalancerSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#add_update_load_balancer_settings.ApiResponseFor200) | successful operation

#### add_update_load_balancer_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**LoadBalancerSettings**](../../models/LoadBalancerSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_ha_stats**
<a name="get_ha_stats"></a>
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} get_ha_stats()

Get HA stats

Gets HA stats on UAG

### Example

```python
import openapi_client
from openapi_client.apis.tags import load_balancer_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = load_balancer_settings_api.LoadBalancerSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get HA stats
        api_response = api_instance.get_ha_stats()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LoadBalancerSettingsApi->get_ha_stats: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_ha_stats.ApiResponseFor200) | successful operation

#### get_ha_stats.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**[any_string_name](#any_string_name)** | dict, frozendict.frozendict,  | frozendict.frozendict,  | any string name can be used but the value must be the correct type | [optional] 

# any_string_name

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_load_balancer_settings**
<a name="get_load_balancer_settings"></a>
> LoadBalancerSettings get_load_balancer_settings()

Get Load balancer settings

Gets the Load balancer settings of UAG

### Example

```python
import openapi_client
from openapi_client.apis.tags import load_balancer_settings_api
from openapi_client.model.load_balancer_settings import LoadBalancerSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = load_balancer_settings_api.LoadBalancerSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get Load balancer settings
        api_response = api_instance.get_load_balancer_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LoadBalancerSettingsApi->get_load_balancer_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_load_balancer_settings.ApiResponseFor200) | successful operation

#### get_load_balancer_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**LoadBalancerSettings**](../../models/LoadBalancerSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_load_balancer_state**
<a name="get_load_balancer_state"></a>
> str get_load_balancer_state()

Get Load balancer state

Gets the Load balancer state on UAG

### Example

```python
import openapi_client
from openapi_client.apis.tags import load_balancer_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = load_balancer_settings_api.LoadBalancerSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get Load balancer state
        api_response = api_instance.get_load_balancer_state()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LoadBalancerSettingsApi->get_load_balancer_state: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_load_balancer_state.ApiResponseFor200) | successful operation

#### get_load_balancer_state.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyTextXml, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyTextXml

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

