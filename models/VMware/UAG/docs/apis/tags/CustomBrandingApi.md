<a name="__pageTop"></a>
# openapi_client.apis.tags.custom_branding_api.CustomBrandingApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_custom_branding_resources**](#get_custom_branding_resources) | **get** /v1/config/customBranding | Get all custom branding details
[**save_custom_branding_settings**](#save_custom_branding_settings) | **put** /v1/config/customBranding/saveCustomBranding | saves custom branding resources

# **get_custom_branding_resources**
<a name="get_custom_branding_resources"></a>
> CustomBrandingSettings get_custom_branding_resources()

Get all custom branding details

Returns custom branding settings.

### Example

```python
import openapi_client
from openapi_client.apis.tags import custom_branding_api
from openapi_client.model.custom_branding_settings import CustomBrandingSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = custom_branding_api.CustomBrandingApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all custom branding details
        api_response = api_instance.get_custom_branding_resources()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CustomBrandingApi->get_custom_branding_resources: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_custom_branding_resources.ApiResponseFor200) | successful operation

#### get_custom_branding_resources.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**CustomBrandingSettings**](../../models/CustomBrandingSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **save_custom_branding_settings**
<a name="save_custom_branding_settings"></a>
> save_custom_branding_settings()

saves custom branding resources

saves custom branding resources

### Example

```python
import openapi_client
from openapi_client.apis.tags import custom_branding_api
from openapi_client.model.custom_branding_settings import CustomBrandingSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = custom_branding_api.CustomBrandingApi(api_client)

    # example passing only optional values
    body = CustomBrandingSettings(
        custom_branding_list=[
            CustomBranding(
                resource_content="resource_content_example",
                resource_name="resource_name_example",
                resource_map_key="resource_map_key_example",
            )
        ],
    )
    try:
        # saves custom branding resources
        api_response = api_instance.save_custom_branding_settings(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling CustomBrandingApi->save_custom_branding_settings: %s\n" % e)
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
[**CustomBrandingSettings**](../../models/CustomBrandingSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#save_custom_branding_settings.ApiResponseForDefault) | successful operation

#### save_custom_branding_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

