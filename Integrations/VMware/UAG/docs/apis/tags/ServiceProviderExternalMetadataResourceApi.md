<a name="__pageTop"></a>
# openapi_client.apis.tags.service_provider_external_metadata_resource_api.ServiceProviderExternalMetadataResourceApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_admin_saml_metadata**](#get_admin_saml_metadata) | **get** /v1/config/sp-ext-metadata/{spExternalHostName} | Get Admin SAML metadata
[**get_sp_metadata**](#get_sp_metadata) | **get** /v1/config/sp-ext-metadata/{spExternalHostName}/{instanceId} | Get SP metadata

# **get_admin_saml_metadata**
<a name="get_admin_saml_metadata"></a>
> IdPExternalMetadataSettings get_admin_saml_metadata(sp_external_host_name)

Get Admin SAML metadata

Get the UAG Admin service metadata for configuring it on IDP

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_external_metadata_resource_api
from openapi_client.model.id_p_external_metadata_settings import IdPExternalMetadataSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_external_metadata_resource_api.ServiceProviderExternalMetadataResourceApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'spExternalHostName': "spExternalHostName_example",
    }
    query_params = {
    }
    try:
        # Get Admin SAML metadata
        api_response = api_instance.get_admin_saml_metadata(
            path_params=path_params,
            query_params=query_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderExternalMetadataResourceApi->get_admin_saml_metadata: %s\n" % e)

    # example passing only optional values
    path_params = {
        'spExternalHostName': "spExternalHostName_example",
    }
    query_params = {
        'idpEntityID': "idpEntityID_example",
    }
    try:
        # Get Admin SAML metadata
        api_response = api_instance.get_admin_saml_metadata(
            path_params=path_params,
            query_params=query_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderExternalMetadataResourceApi->get_admin_saml_metadata: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
query_params | RequestQueryParams | |
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('*/*', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### query_params
#### RequestQueryParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
idpEntityID | IdpEntityIDSchema | | optional


# IdpEntityIDSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
spExternalHostName | SpExternalHostNameSchema | | 

# SpExternalHostNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_admin_saml_metadata.ApiResponseFor200) | successful operation

#### get_admin_saml_metadata.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBody, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBody
Type | Description  | Notes
------------- | ------------- | -------------
[**IdPExternalMetadataSettings**](../../models/IdPExternalMetadataSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_sp_metadata**
<a name="get_sp_metadata"></a>
> IdPExternalMetadataSettings get_sp_metadata(sp_external_host_nameinstance_id)

Get SP metadata

Get the service provider metadata for a single service on the Access Point

### Example

```python
import openapi_client
from openapi_client.apis.tags import service_provider_external_metadata_resource_api
from openapi_client.model.id_p_external_metadata_settings import IdPExternalMetadataSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = service_provider_external_metadata_resource_api.ServiceProviderExternalMetadataResourceApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'spExternalHostName': "spExternalHostName_example",
        'instanceId': "instanceId_example",
    }
    query_params = {
    }
    try:
        # Get SP metadata
        api_response = api_instance.get_sp_metadata(
            path_params=path_params,
            query_params=query_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderExternalMetadataResourceApi->get_sp_metadata: %s\n" % e)

    # example passing only optional values
    path_params = {
        'spExternalHostName': "spExternalHostName_example",
        'instanceId': "instanceId_example",
    }
    query_params = {
        'idpEntityID': "idpEntityID_example",
    }
    try:
        # Get SP metadata
        api_response = api_instance.get_sp_metadata(
            path_params=path_params,
            query_params=query_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServiceProviderExternalMetadataResourceApi->get_sp_metadata: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
query_params | RequestQueryParams | |
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('*/*', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### query_params
#### RequestQueryParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
idpEntityID | IdpEntityIDSchema | | optional


# IdpEntityIDSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
spExternalHostName | SpExternalHostNameSchema | | 
instanceId | InstanceIdSchema | | 

# SpExternalHostNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

# InstanceIdSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_sp_metadata.ApiResponseFor200) | successful operation

#### get_sp_metadata.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBody, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBody
Type | Description  | Notes
------------- | ------------- | -------------
[**IdPExternalMetadataSettings**](../../models/IdPExternalMetadataSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

