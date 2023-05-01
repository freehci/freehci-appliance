<a name="__pageTop"></a>
# openapi_client.apis.tags.uag_feature_settings_api.UAGFeatureSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_feature_settings**](#get_feature_settings) | **get** /v1/config/feature | Get feature settings
[**update_feature_settings**](#update_feature_settings) | **put** /v1/config/feature | Add specified feature&#x27;s settings

# **get_feature_settings**
<a name="get_feature_settings"></a>
> get_feature_settings()

Get feature settings

Get the features map for the UAG by name

### Example

```python
import openapi_client
from openapi_client.apis.tags import uag_feature_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = uag_feature_settings_api.UAGFeatureSettingsApi(api_client)

    # example passing only optional values
    query_params = {
        'featureName': "ALL",
    }
    try:
        # Get feature settings
        api_response = api_instance.get_feature_settings(
            query_params=query_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling UAGFeatureSettingsApi->get_feature_settings: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
query_params | RequestQueryParams | |
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### query_params
#### RequestQueryParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
featureName | FeatureNameSchema | | optional


# FeatureNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | if omitted the server will use the default value of "ALL"

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#get_feature_settings.ApiResponseForDefault) | successful operation

#### get_feature_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_feature_settings**
<a name="update_feature_settings"></a>
> update_feature_settings()

Add specified feature's settings

Add the feature map for the UAG feature

### Example

```python
import openapi_client
from openapi_client.apis.tags import uag_feature_settings_api
from openapi_client.model.uag_feature_flag_info import UAGFeatureFlagInfo
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = uag_feature_settings_api.UAGFeatureSettingsApi(api_client)

    # example passing only optional values
    body = UAGFeatureFlagInfo(
        feature_name="feature_name_example",
        enabled=True,
        environment="PRODUCTION",
    )
    try:
        # Add specified feature's settings
        api_response = api_instance.update_feature_settings(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling UAGFeatureSettingsApi->update_feature_settings: %s\n" % e)
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
[**UAGFeatureFlagInfo**](../../models/UAGFeatureFlagInfo.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#update_feature_settings.ApiResponseForDefault) | successful operation

#### update_feature_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

