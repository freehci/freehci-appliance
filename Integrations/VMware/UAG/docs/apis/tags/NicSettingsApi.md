<a name="__pageTop"></a>
# openapi_client.apis.tags.nic_settings_api.NicSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_all_nic_settings**](#get_all_nic_settings) | **get** /v1/config/nic | Get all NIC settings
[**get_nic_settings**](#get_nic_settings) | **get** /v1/config/nic/{nic} | Get network settings for a specific NIC
[**submit_nic_config**](#submit_nic_config) | **put** /v1/config/nic | Update the specific NIC configuration.

# **get_all_nic_settings**
<a name="get_all_nic_settings"></a>
> NicSettingsList get_all_nic_settings()

Get all NIC settings

Get all the NIC settings.

### Example

```python
import openapi_client
from openapi_client.apis.tags import nic_settings_api
from openapi_client.model.nic_settings_list import NicSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nic_settings_api.NicSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all NIC settings
        api_response = api_instance.get_all_nic_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling NicSettingsApi->get_all_nic_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_nic_settings.ApiResponseFor200) | successful operation

#### get_all_nic_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**NicSettingsList**](../../models/NicSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_nic_settings**
<a name="get_nic_settings"></a>
> get_nic_settings(nic)

Get network settings for a specific NIC

Gets network settings for a specific NIC.

### Example

```python
import openapi_client
from openapi_client.apis.tags import nic_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nic_settings_api.NicSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'nic': "eth0",
    }
    try:
        # Get network settings for a specific NIC
        api_response = api_instance.get_nic_settings(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling NicSettingsApi->get_nic_settings: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
nic | NicSchema | | 

# NicSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["eth0", "eth1", "eth2", ] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#get_nic_settings.ApiResponseForDefault) | successful operation

#### get_nic_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **submit_nic_config**
<a name="submit_nic_config"></a>
> submit_nic_config()

Update the specific NIC configuration.

### Example

```python
import openapi_client
from openapi_client.apis.tags import nic_settings_api
from openapi_client.model.nic_settings import NicSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nic_settings_api.NicSettingsApi(api_client)

    # example passing only optional values
    body = NicSettings(
        ipv4_address="ipv4_address_example",
        ipv4_netmask="ipv4_netmask_example",
        ipv4_default_gateway="ipv4_default_gateway_example",
        nic="eth0",
        allocation_mode="STATICV4",
        ipv4_static_routes="ipv4_static_routes_example",
        custom_config="DHCP^UseDNS=false;DHCP^UseNTP=false;",
    )
    try:
        # Update the specific NIC configuration.
        api_response = api_instance.submit_nic_config(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling NicSettingsApi->submit_nic_config: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**NicSettings**](../../models/NicSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#submit_nic_config.ApiResponseForDefault) | successful operation

#### submit_nic_config.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

