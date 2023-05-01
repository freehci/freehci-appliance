<a name="__pageTop"></a>
# openapi_client.apis.tags.file_upload_settings_api.FileUploadSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_uploaded_resource**](#delete_uploaded_resource) | **delete** /v1/config/resource/deleteUploadedResource/{name}/{fileType} | Delete a custom executable file and its metadata
[**delete_uploaded_resource_associated_with_settings**](#delete_uploaded_resource_associated_with_settings) | **delete** /v1/config/resource/deleteUploadedResource/{settings}/{settingsId}/{fileType} | Delete an uploaded file and its metadata.
[**get_all_resource_settings**](#get_all_resource_settings) | **get** /v1/config/resource | Get all custom executable settings
[**get_resource_settings**](#get_resource_settings) | **get** /v1/config/resource/{name}/{fileType} | Get custom executable settings corresponding to a name and fileType
[**upload_resource**](#upload_resource) | **put** /v1/config/resource/upload | Upload or update file and its metadata.
[**upload_resource_associated_with_settings**](#upload_resource_associated_with_settings) | **put** /v1/config/resource/upload/{settings}/{settingsId}/{fileType} | Upload or update file and its metadata.

# **delete_uploaded_resource**
<a name="delete_uploaded_resource"></a>
> CustomExecutableList delete_uploaded_resource(name_file_type)

Delete a custom executable file and its metadata

### Example

```python
import openapi_client
from openapi_client.apis.tags import file_upload_settings_api
from openapi_client.model.custom_executable_list import CustomExecutableList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = file_upload_settings_api.FileUploadSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
        'fileType': "Windows",
    }
    try:
        # Delete a custom executable file and its metadata
        api_response = api_instance.delete_uploaded_resource(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling FileUploadSettingsApi->delete_uploaded_resource: %s\n" % e)
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
fileType | FileTypeSchema | | 

# NameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# FileTypeSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["Windows", "Mac", ] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#delete_uploaded_resource.ApiResponseFor200) | successful operation

#### delete_uploaded_resource.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**CustomExecutableList**](../../models/CustomExecutableList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_uploaded_resource_associated_with_settings**
<a name="delete_uploaded_resource_associated_with_settings"></a>
> delete_uploaded_resource_associated_with_settings(settingssettings_id_file_type)

Delete an uploaded file and its metadata.

### Example

```python
import openapi_client
from openapi_client.apis.tags import file_upload_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = file_upload_settings_api.FileUploadSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'settings': "settings_example",
        'settingsId': "settingsId_example",
        'fileType': "Windows",
    }
    try:
        # Delete an uploaded file and its metadata.
        api_response = api_instance.delete_uploaded_resource_associated_with_settings(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling FileUploadSettingsApi->delete_uploaded_resource_associated_with_settings: %s\n" % e)
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
settings | SettingsSchema | | 
settingsId | SettingsIdSchema | | 
fileType | FileTypeSchema | | 

# SettingsSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# SettingsIdSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# FileTypeSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["Windows", "Mac", ] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#delete_uploaded_resource_associated_with_settings.ApiResponseForDefault) | successful operation

#### delete_uploaded_resource_associated_with_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_resource_settings**
<a name="get_all_resource_settings"></a>
> CustomExecutableList get_all_resource_settings()

Get all custom executable settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import file_upload_settings_api
from openapi_client.model.custom_executable_list import CustomExecutableList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = file_upload_settings_api.FileUploadSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all custom executable settings
        api_response = api_instance.get_all_resource_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling FileUploadSettingsApi->get_all_resource_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_resource_settings.ApiResponseFor200) | successful operation

#### get_all_resource_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**CustomExecutableList**](../../models/CustomExecutableList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_resource_settings**
<a name="get_resource_settings"></a>
> ResourceSettings get_resource_settings(name_file_type)

Get custom executable settings corresponding to a name and fileType

### Example

```python
import openapi_client
from openapi_client.apis.tags import file_upload_settings_api
from openapi_client.model.resource_settings import ResourceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = file_upload_settings_api.FileUploadSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
        'fileType': "Windows",
    }
    try:
        # Get custom executable settings corresponding to a name and fileType
        api_response = api_instance.get_resource_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling FileUploadSettingsApi->get_resource_settings: %s\n" % e)
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
fileType | FileTypeSchema | | 

# NameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# FileTypeSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["Windows", "Mac", ] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_resource_settings.ApiResponseFor200) | successful operation

#### get_resource_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**ResourceSettings**](../../models/ResourceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **upload_resource**
<a name="upload_resource"></a>
> ResourceSettings upload_resource()

Upload or update file and its metadata.

### Example

```python
import openapi_client
from openapi_client.apis.tags import file_upload_settings_api
from openapi_client.model.resource_settings import ResourceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = file_upload_settings_api.FileUploadSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Upload or update file and its metadata.
        api_response = api_instance.upload_resource()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling FileUploadSettingsApi->upload_resource: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#upload_resource.ApiResponseFor200) | successful operation

#### upload_resource.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**ResourceSettings**](../../models/ResourceSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **upload_resource_associated_with_settings**
<a name="upload_resource_associated_with_settings"></a>
> upload_resource_associated_with_settings(settingssettings_id_file_type)

Upload or update file and its metadata.

### Example

```python
import openapi_client
from openapi_client.apis.tags import file_upload_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = file_upload_settings_api.FileUploadSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'settings': "settings_example",
        'settingsId': "settingsId_example",
        'fileType': "Windows",
    }
    try:
        # Upload or update file and its metadata.
        api_response = api_instance.upload_resource_associated_with_settings(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling FileUploadSettingsApi->upload_resource_associated_with_settings: %s\n" % e)
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
settings | SettingsSchema | | 
settingsId | SettingsIdSchema | | 
fileType | FileTypeSchema | | 

# SettingsSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# SettingsIdSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# FileTypeSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["Windows", "Mac", ] 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#upload_resource_associated_with_settings.ApiResponseForDefault) | successful operation

#### upload_resource_associated_with_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

