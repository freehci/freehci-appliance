<a name="__pageTop"></a>
# openapi_client.apis.tags.workspace_one_intelligence_data_settings_api.WorkspaceOneIntelligenceDataSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_or_update_workspace_one_intelligence_data_settings**](#create_or_update_workspace_one_intelligence_data_settings) | **put** /v1/config/ws1intelligencedata | Add Workspace ONE Intelligence Data settings
[**get_workspace_one_intelligence_data_settings**](#get_workspace_one_intelligence_data_settings) | **get** /v1/config/ws1intelligencedata | Get Workspace ONE Intelligence Data settings

# **create_or_update_workspace_one_intelligence_data_settings**
<a name="create_or_update_workspace_one_intelligence_data_settings"></a>
> create_or_update_workspace_one_intelligence_data_settings()

Add Workspace ONE Intelligence Data settings

Add Workspace ONE Intelligence Data settings for the UAG 

### Example

```python
import openapi_client
from openapi_client.apis.tags import workspace_one_intelligence_data_settings_api
from openapi_client.model.workspace_one_intelligence_data_settings import WorkspaceOneIntelligenceDataSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace_one_intelligence_data_settings_api.WorkspaceOneIntelligenceDataSettingsApi(api_client)

    # example passing only optional values
    body = WorkspaceOneIntelligenceDataSettings(
        enabled=True,
        name="name_example",
        update_interval=1,
    )
    try:
        # Add Workspace ONE Intelligence Data settings
        api_response = api_instance.create_or_update_workspace_one_intelligence_data_settings(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling WorkspaceOneIntelligenceDataSettingsApi->create_or_update_workspace_one_intelligence_data_settings: %s\n" % e)
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
[**WorkspaceOneIntelligenceDataSettings**](../../models/WorkspaceOneIntelligenceDataSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#create_or_update_workspace_one_intelligence_data_settings.ApiResponseForDefault) | successful operation

#### create_or_update_workspace_one_intelligence_data_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_workspace_one_intelligence_data_settings**
<a name="get_workspace_one_intelligence_data_settings"></a>
> get_workspace_one_intelligence_data_settings()

Get Workspace ONE Intelligence Data settings

Get Workspace ONE Intelligence Data settings for the UAG

### Example

```python
import openapi_client
from openapi_client.apis.tags import workspace_one_intelligence_data_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace_one_intelligence_data_settings_api.WorkspaceOneIntelligenceDataSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get Workspace ONE Intelligence Data settings
        api_response = api_instance.get_workspace_one_intelligence_data_settings()
    except openapi_client.ApiException as e:
        print("Exception when calling WorkspaceOneIntelligenceDataSettingsApi->get_workspace_one_intelligence_data_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#get_workspace_one_intelligence_data_settings.ApiResponseForDefault) | successful operation

#### get_workspace_one_intelligence_data_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

