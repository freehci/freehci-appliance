<a name="__pageTop"></a>
# openapi_client.apis.tags.package_update_settings_api.PackageUpdateSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_package_updates_settings**](#get_package_updates_settings) | **get** /v1/config/packageupdates | Get package update settings
[**update_package_updates_settings**](#update_package_updates_settings) | **put** /v1/config/packageupdates | Update package update settings

# **get_package_updates_settings**
<a name="get_package_updates_settings"></a>
> PackageUpdateSettings get_package_updates_settings()

Get package update settings

Get package update settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import package_update_settings_api
from openapi_client.model.package_update_settings import PackageUpdateSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = package_update_settings_api.PackageUpdateSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get package update settings
        api_response = api_instance.get_package_updates_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling PackageUpdateSettingsApi->get_package_updates_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_package_updates_settings.ApiResponseFor200) | successful operation

#### get_package_updates_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**PackageUpdateSettings**](../../models/PackageUpdateSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_package_updates_settings**
<a name="update_package_updates_settings"></a>
> PackageUpdateSettings update_package_updates_settings()

Update package update settings

Create or update package update settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import package_update_settings_api
from openapi_client.model.package_update_settings import PackageUpdateSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = package_update_settings_api.PackageUpdateSettingsApi(api_client)

    # example passing only optional values
    body = PackageUpdateSettings(
        package_updates_scheme="OFF",
        package_updates_osurl="package_updates_osurl_example",
        package_updates_url="package_updates_url_example",
        trusted_certificates=[
            PublicKeyOrCert(
                name="name_example",
                data="data_example",
            )
        ],
    )
    try:
        # Update package update settings
        api_response = api_instance.update_package_updates_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling PackageUpdateSettingsApi->update_package_updates_settings: %s\n" % e)
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
[**PackageUpdateSettings**](../../models/PackageUpdateSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#update_package_updates_settings.ApiResponseFor200) | successful operation

#### update_package_updates_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**PackageUpdateSettings**](../../models/PackageUpdateSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

