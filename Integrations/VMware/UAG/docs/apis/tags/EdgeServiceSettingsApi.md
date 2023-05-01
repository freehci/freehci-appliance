<a name="__pageTop"></a>
# openapi_client.apis.tags.edge_service_settings_api.EdgeServiceSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_or_update_air_watch_cg_edge_service_settings**](#create_or_update_air_watch_cg_edge_service_settings) | **put** /v1/config/edgeservice/contentgateway | Create or update Airwatch Content Gateway settings
[**create_or_update_air_watch_seg_edge_service_settings**](#create_or_update_air_watch_seg_edge_service_settings) | **put** /v1/config/edgeservice/seg | Create or update Airwatch SEG settings
[**create_or_update_air_watch_tunnel_proxy_edge_service_settings**](#create_or_update_air_watch_tunnel_proxy_edge_service_settings) | **put** /v1/config/edgeservice/tunnelproxy | Create or update Airwatch Tunnel proxy settings
[**create_or_update_air_watch_tunnel_server_edge_service_settings**](#create_or_update_air_watch_tunnel_server_edge_service_settings) | **put** /v1/config/edgeservice/tunnelgateway | Create or update Airwatch Tunnel edge server settings
[**create_or_update_view_edge_service_settings**](#create_or_update_view_edge_service_settings) | **put** /v1/config/edgeservice/view | Create or update View edge server settings
[**create_or_update_ws_portal_edge_service_settings**](#create_or_update_ws_portal_edge_service_settings) | **put** /v1/config/edgeservice/webreverseproxy | Create or update Workspace Portal edge server settings
[**delete_edge_service_settings**](#delete_edge_service_settings) | **delete** /v1/config/edgeservice/{edgeServiceType}/{instanceId} | Deletes edge service settings
[**get_all_edge_service_settings**](#get_all_edge_service_settings) | **get** /v1/config/edgeservice | Get all edge service settings
[**get_available_horizon_auth_methods**](#get_available_horizon_auth_methods) | **get** /v1/config/edgeservice/availableHorizonAuthMethods | Get horizon auth methods which are enabled
[**get_edge_service_settings**](#get_edge_service_settings) | **get** /v1/config/edgeservice/{edgeServiceType} | Get edge service settings
[**get_edge_service_settings1**](#get_edge_service_settings1) | **get** /v1/config/edgeservice/findConfiguredEdgeServicesAndAuthMethods | Find the status of configured edge services and auth methods
[**get_edge_service_settings2**](#get_edge_service_settings2) | **get** /v1/config/edgeservice/{edgeServiceType}/{instanceId} | Get edge service settings for a given instance ID

# **create_or_update_air_watch_cg_edge_service_settings**
<a name="create_or_update_air_watch_cg_edge_service_settings"></a>
> AirWatchCGEdgeServiceSettings create_or_update_air_watch_cg_edge_service_settings()

Create or update Airwatch Content Gateway settings

Explicit endpoint for creating a Airwatch Content Gateway edge service settings if it does not exist, otherwise update the existing one.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.air_watch_cg_edge_service_settings import AirWatchCGEdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only optional values
    body = AirWatchCGEdgeServiceSettings(None)
    try:
        # Create or update Airwatch Content Gateway settings
        api_response = api_instance.create_or_update_air_watch_cg_edge_service_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->create_or_update_air_watch_cg_edge_service_settings: %s\n" % e)
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
[**AirWatchCGEdgeServiceSettings**](../../models/AirWatchCGEdgeServiceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_air_watch_cg_edge_service_settings.ApiResponseFor200) | successful operation

#### create_or_update_air_watch_cg_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**AirWatchCGEdgeServiceSettings**](../../models/AirWatchCGEdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **create_or_update_air_watch_seg_edge_service_settings**
<a name="create_or_update_air_watch_seg_edge_service_settings"></a>
> AirWatchSEGEdgeServiceSettings create_or_update_air_watch_seg_edge_service_settings()

Create or update Airwatch SEG settings

Explicit endpoint for creating a Airwatch SEG edge service settings if it does not exist, otherwise update the existing one.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.air_watch_seg_edge_service_settings import AirWatchSEGEdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only optional values
    body = AirWatchSEGEdgeServiceSettings(None)
    try:
        # Create or update Airwatch SEG settings
        api_response = api_instance.create_or_update_air_watch_seg_edge_service_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->create_or_update_air_watch_seg_edge_service_settings: %s\n" % e)
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
[**AirWatchSEGEdgeServiceSettings**](../../models/AirWatchSEGEdgeServiceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_air_watch_seg_edge_service_settings.ApiResponseFor200) | successful operation

#### create_or_update_air_watch_seg_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**AirWatchSEGEdgeServiceSettings**](../../models/AirWatchSEGEdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **create_or_update_air_watch_tunnel_proxy_edge_service_settings**
<a name="create_or_update_air_watch_tunnel_proxy_edge_service_settings"></a>
> AirWatchTunnelProxyEdgeServiceSettings create_or_update_air_watch_tunnel_proxy_edge_service_settings()

Create or update Airwatch Tunnel proxy settings

Explicit endpoint for creating a Airwatch Tunnel Proxy edge service settings if it does not exist, otherwise update the existing one.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.air_watch_tunnel_proxy_edge_service_settings import AirWatchTunnelProxyEdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only optional values
    body = AirWatchTunnelProxyEdgeServiceSettings(None)
    try:
        # Create or update Airwatch Tunnel proxy settings
        api_response = api_instance.create_or_update_air_watch_tunnel_proxy_edge_service_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->create_or_update_air_watch_tunnel_proxy_edge_service_settings: %s\n" % e)
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
[**AirWatchTunnelProxyEdgeServiceSettings**](../../models/AirWatchTunnelProxyEdgeServiceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_air_watch_tunnel_proxy_edge_service_settings.ApiResponseFor200) | successful operation

#### create_or_update_air_watch_tunnel_proxy_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**AirWatchTunnelProxyEdgeServiceSettings**](../../models/AirWatchTunnelProxyEdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **create_or_update_air_watch_tunnel_server_edge_service_settings**
<a name="create_or_update_air_watch_tunnel_server_edge_service_settings"></a>
> AirWatchTunnelServerEdgeServiceSettings create_or_update_air_watch_tunnel_server_edge_service_settings()

Create or update Airwatch Tunnel edge server settings

Explicit endpoint for creating a Airwatch Tunnel Server edge service settings if it does not exist, otherwise update the existing one.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.air_watch_tunnel_server_edge_service_settings import AirWatchTunnelServerEdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only optional values
    body = AirWatchTunnelServerEdgeServiceSettings(None)
    try:
        # Create or update Airwatch Tunnel edge server settings
        api_response = api_instance.create_or_update_air_watch_tunnel_server_edge_service_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->create_or_update_air_watch_tunnel_server_edge_service_settings: %s\n" % e)
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
[**AirWatchTunnelServerEdgeServiceSettings**](../../models/AirWatchTunnelServerEdgeServiceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_air_watch_tunnel_server_edge_service_settings.ApiResponseFor200) | successful operation

#### create_or_update_air_watch_tunnel_server_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**AirWatchTunnelServerEdgeServiceSettings**](../../models/AirWatchTunnelServerEdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **create_or_update_view_edge_service_settings**
<a name="create_or_update_view_edge_service_settings"></a>
> ViewEdgeServiceSettings create_or_update_view_edge_service_settings()

Create or update View edge server settings

Explicit endpoint for creating a View edge service settings if it does not exist, otherwise update the existing one.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.view_edge_service_settings import ViewEdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only optional values
    body = ViewEdgeServiceSettings(None)
    try:
        # Create or update View edge server settings
        api_response = api_instance.create_or_update_view_edge_service_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->create_or_update_view_edge_service_settings: %s\n" % e)
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
[**ViewEdgeServiceSettings**](../../models/ViewEdgeServiceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_view_edge_service_settings.ApiResponseFor200) | successful operation

#### create_or_update_view_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**ViewEdgeServiceSettings**](../../models/ViewEdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **create_or_update_ws_portal_edge_service_settings**
<a name="create_or_update_ws_portal_edge_service_settings"></a>
> WsPortalEdgeServiceSettings create_or_update_ws_portal_edge_service_settings()

Create or update Workspace Portal edge server settings

Explicit endpoint for creating a Workspace Portal edge service settings if it does not exist, otherwise update the existing one.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.ws_portal_edge_service_settings import WsPortalEdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only optional values
    body = WsPortalEdgeServiceSettings(None)
    try:
        # Create or update Workspace Portal edge server settings
        api_response = api_instance.create_or_update_ws_portal_edge_service_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->create_or_update_ws_portal_edge_service_settings: %s\n" % e)
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
[**WsPortalEdgeServiceSettings**](../../models/WsPortalEdgeServiceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_ws_portal_edge_service_settings.ApiResponseFor200) | successful operation

#### create_or_update_ws_portal_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**WsPortalEdgeServiceSettings**](../../models/WsPortalEdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_edge_service_settings**
<a name="delete_edge_service_settings"></a>
> EdgeServiceSettingsList delete_edge_service_settings(edge_service_typeinstance_id)

Deletes edge service settings

Deletes edge service settings for a specified type and instance ID

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.edge_service_settings_list import EdgeServiceSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'edgeServiceType': "WEB_REVERSE_PROXY",
        'instanceId': "instanceId_example",
    }
    try:
        # Deletes edge service settings
        api_response = api_instance.delete_edge_service_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->delete_edge_service_settings: %s\n" % e)
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
edgeServiceType | EdgeServiceTypeSchema | | 
instanceId | InstanceIdSchema | | 

# EdgeServiceTypeSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["WEB_REVERSE_PROXY", ] 

# InstanceIdSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#delete_edge_service_settings.ApiResponseFor200) | successful operation

#### delete_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**EdgeServiceSettingsList**](../../models/EdgeServiceSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_edge_service_settings**
<a name="get_all_edge_service_settings"></a>
> EdgeServiceSettingsList get_all_edge_service_settings()

Get all edge service settings

Get all the edge service settings.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.edge_service_settings_list import EdgeServiceSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all edge service settings
        api_response = api_instance.get_all_edge_service_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->get_all_edge_service_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_edge_service_settings.ApiResponseFor200) | successful operation

#### get_all_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**EdgeServiceSettingsList**](../../models/EdgeServiceSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_available_horizon_auth_methods**
<a name="get_available_horizon_auth_methods"></a>
> [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] get_available_horizon_auth_methods()

Get horizon auth methods which are enabled

Gets list of available horizon auth methods.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get horizon auth methods which are enabled
        api_response = api_instance.get_available_horizon_auth_methods()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->get_available_horizon_auth_methods: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_available_horizon_auth_methods.ApiResponseFor200) | successful operation

#### get_available_horizon_auth_methods.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  |  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[items](#items) | dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

# items

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_edge_service_settings**
<a name="get_edge_service_settings"></a>
> EdgeServiceSettings get_edge_service_settings(edge_service_type)

Get edge service settings

Gets edge service settings for the specified type.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.edge_service_settings import EdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'edgeServiceType': "ROOT",
    }
    try:
        # Get edge service settings
        api_response = api_instance.get_edge_service_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->get_edge_service_settings: %s\n" % e)
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
edgeServiceType | EdgeServiceTypeSchema | | 

# EdgeServiceTypeSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["ROOT", "WEB_REVERSE_PROXY", "VIEW", "TUNNEL_GATEWAY", "TUNNEL_PROXY", "CONTENT_GATEWAY", "SEG", ] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_edge_service_settings.ApiResponseFor200) | successful operation

#### get_edge_service_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**EdgeServiceSettings**](../../models/EdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_edge_service_settings1**
<a name="get_edge_service_settings1"></a>
> ConfiguredEdgeServicesAndAuthMethodList get_edge_service_settings1()

Find the status of configured edge services and auth methods

Gets list of edge services and auth methods with flag to check if it is enabled.

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.configured_edge_services_and_auth_method_list import ConfiguredEdgeServicesAndAuthMethodList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Find the status of configured edge services and auth methods
        api_response = api_instance.get_edge_service_settings1()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->get_edge_service_settings1: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_edge_service_settings1.ApiResponseFor200) | successful operation

#### get_edge_service_settings1.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**ConfiguredEdgeServicesAndAuthMethodList**](../../models/ConfiguredEdgeServicesAndAuthMethodList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_edge_service_settings2**
<a name="get_edge_service_settings2"></a>
> EdgeServiceSettings get_edge_service_settings2(edge_service_typeinstance_id)

Get edge service settings for a given instance ID

Gets edge service settings for the specified type and instance ID. This is used for edge services where multiple instances of same edge service can be configured

### Example

```python
import openapi_client
from openapi_client.apis.tags import edge_service_settings_api
from openapi_client.model.edge_service_settings import EdgeServiceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = edge_service_settings_api.EdgeServiceSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'edgeServiceType': "WEB_REVERSE_PROXY",
        'instanceId': "instanceId_example",
    }
    try:
        # Get edge service settings for a given instance ID
        api_response = api_instance.get_edge_service_settings2(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling EdgeServiceSettingsApi->get_edge_service_settings2: %s\n" % e)
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
edgeServiceType | EdgeServiceTypeSchema | | 
instanceId | InstanceIdSchema | | 

# EdgeServiceTypeSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["WEB_REVERSE_PROXY", ] 

# InstanceIdSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_edge_service_settings2.ApiResponseFor200) | successful operation

#### get_edge_service_settings2.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**EdgeServiceSettings**](../../models/EdgeServiceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

