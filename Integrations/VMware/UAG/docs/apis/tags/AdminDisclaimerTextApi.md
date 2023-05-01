<a name="__pageTop"></a>
# openapi_client.apis.tags.admin_disclaimer_text_api.AdminDisclaimerTextApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_admin_disclaimer_text**](#get_admin_disclaimer_text) | **get** /v1/config/disclaimer | Get Admin Disclaimer Text

# **get_admin_disclaimer_text**
<a name="get_admin_disclaimer_text"></a>
> str get_admin_disclaimer_text()

Get Admin Disclaimer Text

Get the Admin Disclaimer Text info for the Unified Access Gateway

### Example

```python
import openapi_client
from openapi_client.apis.tags import admin_disclaimer_text_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = admin_disclaimer_text_api.AdminDisclaimerTextApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get Admin Disclaimer Text
        api_response = api_instance.get_admin_disclaimer_text()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AdminDisclaimerTextApi->get_admin_disclaimer_text: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_admin_disclaimer_text.ApiResponseFor200) | successful operation

#### get_admin_disclaimer_text.ApiResponseFor200
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

