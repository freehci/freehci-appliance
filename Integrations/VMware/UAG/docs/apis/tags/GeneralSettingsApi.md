<a name="__pageTop"></a>
# openapi_client.apis.tags.general_settings_api.GeneralSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_general_settings**](#get_general_settings) | **get** /v1/config/general | Get general settings

# **get_general_settings**
<a name="get_general_settings"></a>
> GeneralSettings get_general_settings()

Get general settings

Get the settings which contain configuration info for the Access Point

### Example

```python
import openapi_client
from openapi_client.apis.tags import general_settings_api
from openapi_client.model.general_settings import GeneralSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = general_settings_api.GeneralSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get general settings
        api_response = api_instance.get_general_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling GeneralSettingsApi->get_general_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_general_settings.ApiResponseFor200) | successful operation

#### get_general_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**GeneralSettings**](../../models/GeneralSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

