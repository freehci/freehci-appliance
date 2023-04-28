<a name="__pageTop"></a>
# openapi_client.apis.tags.syslog_server_settings_api.SyslogServerSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_or_update_syslog_settings**](#create_or_update_syslog_settings) | **put** /v1/config/syslog | Create/Update syslog settings
[**delete_syslog_server_settings**](#delete_syslog_server_settings) | **delete** /v1/config/syslog/{hostName} | Delete specific server Settings
[**get_syslog_server_settings**](#get_syslog_server_settings) | **get** /v1/config/syslog/{hostName} | Get specific syslog server Settings
[**get_syslog_settings**](#get_syslog_settings) | **get** /v1/config/syslog | Get all Syslog server  Settings
[**update_syslog_server_settings**](#update_syslog_server_settings) | **put** /v1/config/syslog/{hostName} | Create/update specific syslog server settings

# **create_or_update_syslog_settings**
<a name="create_or_update_syslog_settings"></a>
> SyslogSettings create_or_update_syslog_settings()

Create/Update syslog settings

Create/Update syslog settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import syslog_server_settings_api
from openapi_client.model.syslog_settings import SyslogSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = syslog_server_settings_api.SyslogServerSettingsApi(api_client)

    # example passing only optional values
    body = SyslogSettings(
        syslog_server_settings=[
            SyslogServerSettings(
                syslog_category="syslog_category_example",
                syslog_category_list=[
                    "ALL"
                ],
                syslog_format="TEXT",
                sys_log_type="UDP",
                syslog_system_messages_enabled_v2=True,
                syslog_url="syslog_url_example",
                mqtt_topic="mqtt_topic_example",
                syslog_setting_name="zBAMDTMv",
                tls_syslog_server_settings=TlsSyslogServerSettings(
                    hostname="hostname_example",
                    port=1,
                    accepted_peer="accepted_peer_example",
                    syslog_server_ca_cert_pem_v2="syslog_server_ca_cert_pem_v2_example",
                    syslog_client_cert_pem_v2="syslog_client_cert_pem_v2_example",
                    syslog_client_cert_key_pem_v2="syslog_client_cert_key_pem_v2_example",
                ),
                tls_mqtt_server_settings=TlsMqttServerSettings(
                    mqtt_client_cert_cert_pem="mqtt_client_cert_cert_pem_example",
                    mqtt_client_cert_key_pem="mqtt_client_cert_key_pem_example",
                    mqtt_server_ca_cert_pem="mqtt_server_ca_cert_pem_example",
                ),
            )
        ],
    )
    try:
        # Create/Update syslog settings
        api_response = api_instance.create_or_update_syslog_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SyslogServerSettingsApi->create_or_update_syslog_settings: %s\n" % e)
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
[**SyslogSettings**](../../models/SyslogSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_syslog_settings.ApiResponseFor200) | successful operation

#### create_or_update_syslog_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SyslogSettings**](../../models/SyslogSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_syslog_server_settings**
<a name="delete_syslog_server_settings"></a>
> SyslogSettings delete_syslog_server_settings(host_name)

Delete specific server Settings

Delete server settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import syslog_server_settings_api
from openapi_client.model.syslog_settings import SyslogSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = syslog_server_settings_api.SyslogServerSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'hostName': "hostName_example",
    }
    try:
        # Delete specific server Settings
        api_response = api_instance.delete_syslog_server_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SyslogServerSettingsApi->delete_syslog_server_settings: %s\n" % e)
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
hostName | HostNameSchema | | 

# HostNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#delete_syslog_server_settings.ApiResponseFor200) | successful operation

#### delete_syslog_server_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SyslogSettings**](../../models/SyslogSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_syslog_server_settings**
<a name="get_syslog_server_settings"></a>
> SyslogServerSettings get_syslog_server_settings(host_name)

Get specific syslog server Settings

Get SyslogServer Settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import syslog_server_settings_api
from openapi_client.model.syslog_server_settings import SyslogServerSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = syslog_server_settings_api.SyslogServerSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'hostName': "hostName_example",
    }
    try:
        # Get specific syslog server Settings
        api_response = api_instance.get_syslog_server_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SyslogServerSettingsApi->get_syslog_server_settings: %s\n" % e)
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
hostName | HostNameSchema | | 

# HostNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_syslog_server_settings.ApiResponseFor200) | successful operation

#### get_syslog_server_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SyslogServerSettings**](../../models/SyslogServerSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_syslog_settings**
<a name="get_syslog_settings"></a>
> SyslogSettings get_syslog_settings()

Get all Syslog server  Settings

Get the complete info includes all syslog server settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import syslog_server_settings_api
from openapi_client.model.syslog_settings import SyslogSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = syslog_server_settings_api.SyslogServerSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all Syslog server  Settings
        api_response = api_instance.get_syslog_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SyslogServerSettingsApi->get_syslog_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_syslog_settings.ApiResponseFor200) | successful operation

#### get_syslog_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SyslogSettings**](../../models/SyslogSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_syslog_server_settings**
<a name="update_syslog_server_settings"></a>
> SyslogSettings update_syslog_server_settings(host_name)

Create/update specific syslog server settings

create/update existing syslog server settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import syslog_server_settings_api
from openapi_client.model.syslog_server_settings import SyslogServerSettings
from openapi_client.model.syslog_settings import SyslogSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = syslog_server_settings_api.SyslogServerSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'hostName': "hostName_example",
    }
    try:
        # Create/update specific syslog server settings
        api_response = api_instance.update_syslog_server_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SyslogServerSettingsApi->update_syslog_server_settings: %s\n" % e)

    # example passing only optional values
    path_params = {
        'hostName': "hostName_example",
    }
    body = SyslogServerSettings(
        syslog_category="syslog_category_example",
        syslog_category_list=[
            "ALL"
        ],
        syslog_format="TEXT",
        sys_log_type="UDP",
        syslog_system_messages_enabled_v2=True,
        syslog_url="syslog_url_example",
        mqtt_topic="mqtt_topic_example",
        syslog_setting_name="zBAMDTMv",
        tls_syslog_server_settings=TlsSyslogServerSettings(
            hostname="hostname_example",
            port=1,
            accepted_peer="accepted_peer_example",
            syslog_server_ca_cert_pem_v2="syslog_server_ca_cert_pem_v2_example",
            syslog_client_cert_pem_v2="syslog_client_cert_pem_v2_example",
            syslog_client_cert_key_pem_v2="syslog_client_cert_key_pem_v2_example",
        ),
        tls_mqtt_server_settings=TlsMqttServerSettings(
            mqtt_client_cert_cert_pem="mqtt_client_cert_cert_pem_example",
            mqtt_client_cert_key_pem="mqtt_client_cert_key_pem_example",
            mqtt_server_ca_cert_pem="mqtt_server_ca_cert_pem_example",
        ),
    )
    try:
        # Create/update specific syslog server settings
        api_response = api_instance.update_syslog_server_settings(
            path_params=path_params,
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SyslogServerSettingsApi->update_syslog_server_settings: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
path_params | RequestPathParams | |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SyslogServerSettings**](../../models/SyslogServerSettings.md) |  | 


### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
hostName | HostNameSchema | | 

# HostNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#update_syslog_server_settings.ApiResponseFor200) | successful operation

#### update_syslog_server_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SyslogSettings**](../../models/SyslogSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

