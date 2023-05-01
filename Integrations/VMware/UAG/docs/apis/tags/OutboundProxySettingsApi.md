<a name="__pageTop"></a>
# openapi_client.apis.tags.outbound_proxy_settings_api.OutboundProxySettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_outbound_proxy_settings**](#create_outbound_proxy_settings) | **post** /v1/config/proxy | Create Proxy settings
[**delete_proxy_settings_given_by_name**](#delete_proxy_settings_given_by_name) | **delete** /v1/config/proxy/{name} | Delete Proxy Settings
[**get_all_proxy_settings**](#get_all_proxy_settings) | **get** /v1/config/proxy | Get all Proxy Settings
[**get_outbound_proxy_settings**](#get_outbound_proxy_settings) | **get** /v1/config/proxy/{name} | Get Proxy Settings
[**update_outbound_proxy_settings**](#update_outbound_proxy_settings) | **put** /v1/config/proxy | Update Proxy settings

# **create_outbound_proxy_settings**
<a name="create_outbound_proxy_settings"></a>
> OutboundProxySettings create_outbound_proxy_settings()

Create Proxy settings

Create Proxy settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import outbound_proxy_settings_api
from openapi_client.model.outbound_proxy_settings import OutboundProxySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = outbound_proxy_settings_api.OutboundProxySettingsApi(api_client)

    # example passing only optional values
    body = OutboundProxySettings(
        name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
        proxy_type="HTTP",
        proxy_url="proxy_url_example",
        included_hosts=[
            "included_hosts_example"
        ],
        trusted_certificates=[
            PublicKeyOrCert(
                name="name_example",
                data="data_example",
            )
        ],
    )
    try:
        # Create Proxy settings
        api_response = api_instance.create_outbound_proxy_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling OutboundProxySettingsApi->create_outbound_proxy_settings: %s\n" % e)
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
[**OutboundProxySettings**](../../models/OutboundProxySettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_outbound_proxy_settings.ApiResponseFor200) | successful operation

#### create_outbound_proxy_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OutboundProxySettings**](../../models/OutboundProxySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_proxy_settings_given_by_name**
<a name="delete_proxy_settings_given_by_name"></a>
> OutboundProxySettingsList delete_proxy_settings_given_by_name(name)

Delete Proxy Settings

Delete existing Proxy settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import outbound_proxy_settings_api
from openapi_client.model.outbound_proxy_settings_list import OutboundProxySettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = outbound_proxy_settings_api.OutboundProxySettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Delete Proxy Settings
        api_response = api_instance.delete_proxy_settings_given_by_name(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling OutboundProxySettingsApi->delete_proxy_settings_given_by_name: %s\n" % e)
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
200 | [ApiResponseFor200](#delete_proxy_settings_given_by_name.ApiResponseFor200) | successful operation

#### delete_proxy_settings_given_by_name.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OutboundProxySettingsList**](../../models/OutboundProxySettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_proxy_settings**
<a name="get_all_proxy_settings"></a>
> OutboundProxySettingsList get_all_proxy_settings()

Get all Proxy Settings

Get the list of all Proxy Settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import outbound_proxy_settings_api
from openapi_client.model.outbound_proxy_settings_list import OutboundProxySettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = outbound_proxy_settings_api.OutboundProxySettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all Proxy Settings
        api_response = api_instance.get_all_proxy_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling OutboundProxySettingsApi->get_all_proxy_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_proxy_settings.ApiResponseFor200) | successful operation

#### get_all_proxy_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OutboundProxySettingsList**](../../models/OutboundProxySettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_outbound_proxy_settings**
<a name="get_outbound_proxy_settings"></a>
> OutboundProxySettings get_outbound_proxy_settings(name)

Get Proxy Settings

Get Proxy Settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import outbound_proxy_settings_api
from openapi_client.model.outbound_proxy_settings import OutboundProxySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = outbound_proxy_settings_api.OutboundProxySettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Get Proxy Settings
        api_response = api_instance.get_outbound_proxy_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling OutboundProxySettingsApi->get_outbound_proxy_settings: %s\n" % e)
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
200 | [ApiResponseFor200](#get_outbound_proxy_settings.ApiResponseFor200) | successful operation

#### get_outbound_proxy_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OutboundProxySettings**](../../models/OutboundProxySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_outbound_proxy_settings**
<a name="update_outbound_proxy_settings"></a>
> OutboundProxySettings update_outbound_proxy_settings()

Update Proxy settings

Update existing Proxy settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import outbound_proxy_settings_api
from openapi_client.model.outbound_proxy_settings import OutboundProxySettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = outbound_proxy_settings_api.OutboundProxySettingsApi(api_client)

    # example passing only optional values
    body = OutboundProxySettings(
        name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
        proxy_type="HTTP",
        proxy_url="proxy_url_example",
        included_hosts=[
            "included_hosts_example"
        ],
        trusted_certificates=[
            PublicKeyOrCert(
                name="name_example",
                data="data_example",
            )
        ],
    )
    try:
        # Update Proxy settings
        api_response = api_instance.update_outbound_proxy_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling OutboundProxySettingsApi->update_outbound_proxy_settings: %s\n" % e)
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
[**OutboundProxySettings**](../../models/OutboundProxySettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#update_outbound_proxy_settings.ApiResponseFor200) | successful operation

#### update_outbound_proxy_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**OutboundProxySettings**](../../models/OutboundProxySettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

