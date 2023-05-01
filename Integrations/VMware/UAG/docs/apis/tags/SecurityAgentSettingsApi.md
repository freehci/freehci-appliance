<a name="__pageTop"></a>
# openapi_client.apis.tags.security_agent_settings_api.SecurityAgentSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_security_agent_settings**](#delete_security_agent_settings) | **delete** /v1/config/securityAgent/{name} | Delete a Security Agent
[**get_configurable_security_agents**](#get_configurable_security_agents) | **get** /v1/config/securityAgent/available | Get list of security agents that can be configured. This excludes the agents that are already configured
[**get_configured_security_agents**](#get_configured_security_agents) | **get** /v1/config/securityAgent/configured | Get all the configured security agents
[**get_security_agent_settings**](#get_security_agent_settings) | **get** /v1/config/securityAgent/{name} | Get the security agent setting specified by the name
[**put_security_agent_settings**](#put_security_agent_settings) | **put** /v1/config/securityAgent/{name} | Add or update Security Agent Settings

# **delete_security_agent_settings**
<a name="delete_security_agent_settings"></a>
> SecurityAgentSettings delete_security_agent_settings(name)

Delete a Security Agent

### Example

```python
import openapi_client
from openapi_client.apis.tags import security_agent_settings_api
from openapi_client.model.security_agent_settings import SecurityAgentSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = security_agent_settings_api.SecurityAgentSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Delete a Security Agent
        api_response = api_instance.delete_security_agent_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SecurityAgentSettingsApi->delete_security_agent_settings: %s\n" % e)
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
200 | [ApiResponseFor200](#delete_security_agent_settings.ApiResponseFor200) | successful operation

#### delete_security_agent_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SecurityAgentSettings**](../../models/SecurityAgentSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_configurable_security_agents**
<a name="get_configurable_security_agents"></a>
> [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] get_configurable_security_agents()

Get list of security agents that can be configured. This excludes the agents that are already configured

### Example

```python
import openapi_client
from openapi_client.apis.tags import security_agent_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = security_agent_settings_api.SecurityAgentSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get list of security agents that can be configured. This excludes the agents that are already configured
        api_response = api_instance.get_configurable_security_agents()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SecurityAgentSettingsApi->get_configurable_security_agents: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_configurable_security_agents.ApiResponseFor200) | successful operation

#### get_configurable_security_agents.ApiResponseFor200
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

# **get_configured_security_agents**
<a name="get_configured_security_agents"></a>
> SecurityAgentSettingsList get_configured_security_agents()

Get all the configured security agents

### Example

```python
import openapi_client
from openapi_client.apis.tags import security_agent_settings_api
from openapi_client.model.security_agent_settings_list import SecurityAgentSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = security_agent_settings_api.SecurityAgentSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all the configured security agents
        api_response = api_instance.get_configured_security_agents()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SecurityAgentSettingsApi->get_configured_security_agents: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_configured_security_agents.ApiResponseFor200) | successful operation

#### get_configured_security_agents.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SecurityAgentSettingsList**](../../models/SecurityAgentSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_security_agent_settings**
<a name="get_security_agent_settings"></a>
> SecurityAgentSettings get_security_agent_settings(name)

Get the security agent setting specified by the name

### Example

```python
import openapi_client
from openapi_client.apis.tags import security_agent_settings_api
from openapi_client.model.security_agent_settings import SecurityAgentSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = security_agent_settings_api.SecurityAgentSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Get the security agent setting specified by the name
        api_response = api_instance.get_security_agent_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SecurityAgentSettingsApi->get_security_agent_settings: %s\n" % e)
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
200 | [ApiResponseFor200](#get_security_agent_settings.ApiResponseFor200) | successful operation

#### get_security_agent_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SecurityAgentSettings**](../../models/SecurityAgentSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **put_security_agent_settings**
<a name="put_security_agent_settings"></a>
> SecurityAgentSettings put_security_agent_settings()

Add or update Security Agent Settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import security_agent_settings_api
from openapi_client.model.security_agent_settings import SecurityAgentSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = security_agent_settings_api.SecurityAgentSettingsApi(api_client)

    # example passing only optional values
    body = SecurityAgentSettings()
    try:
        # Add or update Security Agent Settings
        api_response = api_instance.put_security_agent_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SecurityAgentSettingsApi->put_security_agent_settings: %s\n" % e)
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
[**SecurityAgentSettings**](../../models/SecurityAgentSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#put_security_agent_settings.ApiResponseFor200) | successful operation

#### put_security_agent_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SecurityAgentSettings**](../../models/SecurityAgentSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

