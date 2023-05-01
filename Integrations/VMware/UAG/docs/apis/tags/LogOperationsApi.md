<a name="__pageTop"></a>
# openapi_client.apis.tags.log_operations_api.LogOperationsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_seg_redirect_mapping**](#delete_seg_redirect_mapping) | **delete** /v1/monitor/seg/cache/{id} | Delete SEG redirect mapping
[**get_log_archive**](#get_log_archive) | **get** /v1/monitor/support-archive | Get log archive
[**get_log_levels**](#get_log_levels) | **get** /v1/monitor/getLogLevels | Get log levels
[**get_seg_diagnostic_stats**](#get_seg_diagnostic_stats) | **get** /v1/monitor/seg/diagnostics/{identifier} | Get SEG Stats
[**get_seg_health_stats**](#get_seg_health_stats) | **get** /v1/monitor/seg/healthStats | SEG Health Stats
[**get_stats**](#get_stats) | **get** /v1/monitor/stats | Get Stats
[**reset_log_levels**](#reset_log_levels) | **get** /v1/monitor/resetLogLevels | Reset log levels
[**set_log_levels**](#set_log_levels) | **put** /v1/monitor/setLogLevels | Set log levels
[**set_utserver_log_level**](#set_utserver_log_level) | **get** /v1/monitor/setUtserverLogLevel/{logLevel} | Set UT server log level

# **delete_seg_redirect_mapping**
<a name="delete_seg_redirect_mapping"></a>
> str delete_seg_redirect_mapping(id)

Delete SEG redirect mapping

Delete cached email redirect mapping on SEG

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'id': "id_example",
    }
    try:
        # Delete SEG redirect mapping
        api_response = api_instance.delete_seg_redirect_mapping(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->delete_seg_redirect_mapping: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('*/*', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
id | IdSchema | | 

# IdSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#delete_seg_redirect_mapping.ApiResponseFor200) | successful operation

#### delete_seg_redirect_mapping.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBody, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBody

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_log_archive**
<a name="get_log_archive"></a>
> str get_log_archive()

Get log archive

Gets a ZIP archive of all Access Point log files. NOTE: this API does not work through the Swagger UI or Postman. To experiment with the API, enter the URL directly into the browser. e.g. https://accesspoint:9443/rest/v1/monitor/support-archive

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get log archive
        api_response = api_instance.get_log_archive()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->get_log_archive: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_log_archive.ApiResponseFor200) | successful operation

#### get_log_archive.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationZip, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationZip

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_log_levels**
<a name="get_log_levels"></a>
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} get_log_levels()

Get log levels

Get modulewise log severity levels

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get log levels
        api_response = api_instance.get_log_levels()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->get_log_levels: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_log_levels.ApiResponseFor200) | successful operation

#### get_log_levels.ApiResponseFor200
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

# **get_seg_diagnostic_stats**
<a name="get_seg_diagnostic_stats"></a>
> str get_seg_diagnostic_stats(identifier)

Get SEG Stats

View/Download SEG cached policy data/diagnostic statistics

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'identifier': [
        "identifier_example"
    ],
    }
    try:
        # Get SEG Stats
        api_response = api_instance.get_seg_diagnostic_stats(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->get_seg_diagnostic_stats: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('application/zip', 'application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
identifier | IdentifierSchema | | 

# IdentifierSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  |  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
items | str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_seg_diagnostic_stats.ApiResponseFor200) | successful operation

#### get_seg_diagnostic_stats.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationZip, SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationZip

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# SchemaFor200ResponseBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_seg_health_stats**
<a name="get_seg_health_stats"></a>
> str get_seg_health_stats()

SEG Health Stats

View SEG server diagnostic and health statistics

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # SEG Health Stats
        api_response = api_instance.get_seg_health_stats()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->get_seg_health_stats: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_seg_health_stats.ApiResponseFor200) | successful operation

#### get_seg_health_stats.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_stats**
<a name="get_stats"></a>
> str get_stats()

Get Stats

Get Stats

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get Stats
        api_response = api_instance.get_stats()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->get_stats: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_stats.ApiResponseFor200) | successful operation

#### get_stats.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationXml, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationXml

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **reset_log_levels**
<a name="reset_log_levels"></a>
> str reset_log_levels()

Reset log levels

Reset all log severity levels to info

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Reset log levels
        api_response = api_instance.reset_log_levels()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->reset_log_levels: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#reset_log_levels.ApiResponseFor200) | successful operation

#### reset_log_levels.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyTextPlain, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyTextPlain

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **set_log_levels**
<a name="set_log_levels"></a>
> {str: ({str: (bool, date, datetime, dict, float, int, list, str, none_type)},)} set_log_levels()

Set log levels

Set modulewise log severity levels.  Log levels set can be: error, warn, info, debug, trace for any of the modules.  To set all modules to debug, send {\"all\" :\"debug\"}.  Keys for api to set log levels for modules,  ALL, ADMIN, HORIZON_ALL, HORIZON_XMLAPI, HORIZON_AUTH, HORIZON_BLAST,  HORIZON_TUNNEL, HORIZON_PCOIP, HORIZON_UTSERVER, HORIZON_COMPLIANCE, WRP_ALL.  

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example passing only optional values
    body = dict(
        "key": "key_example",
    )
    try:
        # Set log levels
        api_response = api_instance.set_log_levels(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->set_log_levels: %s\n" % e)
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

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**any_string_name** | str,  | str,  | any string name can be used but the value must be the correct type | [optional] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#set_log_levels.ApiResponseFor200) | successful operation

#### set_log_levels.ApiResponseFor200
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

# **set_utserver_log_level**
<a name="set_utserver_log_level"></a>
> str set_utserver_log_level(log_level)

Set UT server log level

Set Log Level of UDP Tunnel server. 

### Example

```python
import openapi_client
from openapi_client.apis.tags import log_operations_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = log_operations_api.LogOperationsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'logLevel': "ERROR",
    }
    try:
        # Set UT server log level
        api_response = api_instance.set_utserver_log_level(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling LogOperationsApi->set_utserver_log_level: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('text/plain', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
logLevel | LogLevelSchema | | 

# LogLevelSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["ERROR", "WARN", "INFO", "DEBUG", "TRACE", ] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#set_utserver_log_level.ApiResponseFor200) | successful operation

#### set_utserver_log_level.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyTextPlain, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyTextPlain

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

