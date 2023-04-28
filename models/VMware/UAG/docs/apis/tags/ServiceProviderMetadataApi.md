<a name="__pageTop"></a>
# openapi_client.apis.tags.service_provider_metadata_api.ServiceProviderMetadataApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_sp_metadata**](#create_sp_metadata) | **post** /v1/config/sp-metadata/{name} | Add new SP metadata
[**delete_sp_metadata**](#delete_sp_metadata) | **delete** /v1/config/sp-metadata/{name} | Delete SP metadata
[**get_sp_metadata1**](#get_sp_metadata1) | **get** /v1/config/sp-metadata/{name} | Get SP metadata
[**get_sp_metadata_list**](#get_sp_metadata_list) | **get** /v1/config/sp-metadata | Get all of the SP metadata
[**put_sp_metadata**](#put_sp_metadata) | **put** /v1/config/sp-metadata/{name} | Update SP metadata
[**put_sp_metadata_list**](#put_sp_metadata_list) | **put** /v1/config/sp-metadata | Put all of the SP metadata

# **create_sp_metadata**
<a name="create_sp_metadata"></a>
> SpMediaType create_sp_metadata(name)

Add new SP metadata

Add the metadata XML for a new service provider into Unified Access Gateway.

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_metadata_api
from openapi_client.model.sp_media_type import SpMediaType
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_metadata_api.ServiceProviderMetadataApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Add new SP metadata
        api_response = api_instance.create_sp_metadata(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->create_sp_metadata: %s\n" % e)

    # example passing only optional values
    path_params = {
        'name': "name_example",
    }
    body = "body_example"
    try:
        # Add new SP metadata
        api_response = api_instance.create_sp_metadata(
            path_params=path_params,
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->create_sp_metadata: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyTextXml, Unset] | optional, default is unset |
path_params | RequestPathParams | |
content_type | str | optional, default is 'text/xml' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyTextXml

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

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
200 | [ApiResponseFor200](#create_sp_metadata.ApiResponseFor200) | successful operation

#### create_sp_metadata.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SpMediaType**](../../models/SpMediaType.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_sp_metadata**
<a name="delete_sp_metadata"></a>
> delete_sp_metadata(name)

Delete SP metadata

Delete the metadata XML for a specific SP that has been stored in Unified Access Gateway

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_metadata_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_metadata_api.ServiceProviderMetadataApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Delete SP metadata
        api_response = api_instance.delete_sp_metadata(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->delete_sp_metadata: %s\n" % e)
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
default | [ApiResponseForDefault](#delete_sp_metadata.ApiResponseForDefault) | successful operation

#### delete_sp_metadata.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_sp_metadata1**
<a name="get_sp_metadata1"></a>
> str get_sp_metadata1(name)

Get SP metadata

Get the metadata XML for a specific service provider that has been stored in Unified Access Gateway,

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_metadata_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_metadata_api.ServiceProviderMetadataApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Get SP metadata
        api_response = api_instance.get_sp_metadata1(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->get_sp_metadata1: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('text/xml', ) | Tells the server the content type(s) that are accepted by the client
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
200 | [ApiResponseFor200](#get_sp_metadata1.ApiResponseFor200) | successful operation

#### get_sp_metadata1.ApiResponseFor200
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

# **get_sp_metadata_list**
<a name="get_sp_metadata_list"></a>
> SpMediaTypes get_sp_metadata_list()

Get all of the SP metadata

Get all of the service provider metadata XML for the Unified Access Gateway.

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_metadata_api
from openapi_client.model.sp_media_types import SpMediaTypes
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_metadata_api.ServiceProviderMetadataApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all of the SP metadata
        api_response = api_instance.get_sp_metadata_list()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->get_sp_metadata_list: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_sp_metadata_list.ApiResponseFor200) | successful operation

#### get_sp_metadata_list.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SpMediaTypes**](../../models/SpMediaTypes.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **put_sp_metadata**
<a name="put_sp_metadata"></a>
> SpMediaType put_sp_metadata(name)

Update SP metadata

Update the metadata XML for a specific service provider into Unified Access Gateway.

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_metadata_api
from openapi_client.model.sp_media_type import SpMediaType
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_metadata_api.ServiceProviderMetadataApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Update SP metadata
        api_response = api_instance.put_sp_metadata(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->put_sp_metadata: %s\n" % e)

    # example passing only optional values
    path_params = {
        'name': "name_example",
    }
    body = "body_example"
    try:
        # Update SP metadata
        api_response = api_instance.put_sp_metadata(
            path_params=path_params,
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->put_sp_metadata: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyTextXml, Unset] | optional, default is unset |
path_params | RequestPathParams | |
content_type | str | optional, default is 'text/xml' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyTextXml

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

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
200 | [ApiResponseFor200](#put_sp_metadata.ApiResponseFor200) | successful operation

#### put_sp_metadata.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SpMediaType**](../../models/SpMediaType.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **put_sp_metadata_list**
<a name="put_sp_metadata_list"></a>
> SpMediaTypes put_sp_metadata_list()

Put all of the SP metadata

Put all of the service provider metadata XML for the Unified Access Gateway, deleting any existing metadata.

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_metadata_api
from openapi_client.model.sp_media_types import SpMediaTypes
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_metadata_api.ServiceProviderMetadataApi(api_client)

    # example passing only optional values
    body = SpMediaTypes(
        items=[
            SpMediaType(
                sp_name="sp_name_example",
                metadata_xml="metadata_xml_example",
                assertion_lifetime=1,
                links=dict(
                    "key": Link(
                        href="href_example",
                        params=dict(),
                    ),
                ),
            )
        ],
        links=dict(),
    )
    try:
        # Put all of the SP metadata
        api_response = api_instance.put_sp_metadata_list(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderMetadataApi->put_sp_metadata_list: %s\n" % e)
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
[**SpMediaTypes**](../../models/SpMediaTypes.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#put_sp_metadata_list.ApiResponseFor200) | successful operation

#### put_sp_metadata_list.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SpMediaTypes**](../../models/SpMediaTypes.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

