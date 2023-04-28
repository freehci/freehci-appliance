<a name="__pageTop"></a>
# openapi_client.apis.tags.identity_provider_external_metadata_api.IdentityProviderExternalMetadataApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_idp_metadata**](#get_idp_metadata) | **get** /v1/config/idp-ext-metadata/{entityID}(.*) | Get IdP metadata
[**get_idp_metadata1**](#get_idp_metadata1) | **get** /v1/config/idp-ext-metadata | Get IdP metadata list
[**put_idp_metadata**](#put_idp_metadata) | **put** /v1/config/idp-ext-metadata | Put IdP metadata

# **get_idp_metadata**
<a name="get_idp_metadata"></a>
> IdPExternalMetadataSettings get_idp_metadata(entity_id)

Get IdP metadata

Get the external identity provider metadata for a single entity ID for the Access Point

### Example

```python
import openapi_client
from openapi_client.apis.tags import identity_provider_external_metadata_api
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
    api_instance = identity_provider_external_metadata_api.IdentityProviderExternalMetadataApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'entityID': "entityID_example",
    }
    try:
        # Get IdP metadata
        api_response = api_instance.get_idp_metadata(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IdentityProviderExternalMetadataApi->get_idp_metadata: %s\n" % e)
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
entityID | EntityIDSchema | | 

# EntityIDSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_idp_metadata.ApiResponseFor200) | successful operation

#### get_idp_metadata.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**IdPExternalMetadataSettings**](../../models/IdPExternalMetadataSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_idp_metadata1**
<a name="get_idp_metadata1"></a>
> IdPExternalMetadataSettingsList get_idp_metadata1()

Get IdP metadata list

Get the external identity provider metadata list for the Access Point

### Example

```python
import openapi_client
from openapi_client.apis.tags import identity_provider_external_metadata_api
from openapi_client.model.id_p_external_metadata_settings_list import IdPExternalMetadataSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_provider_external_metadata_api.IdentityProviderExternalMetadataApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get IdP metadata list
        api_response = api_instance.get_idp_metadata1()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IdentityProviderExternalMetadataApi->get_idp_metadata1: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_idp_metadata1.ApiResponseFor200) | successful operation

#### get_idp_metadata1.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**IdPExternalMetadataSettingsList**](../../models/IdPExternalMetadataSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **put_idp_metadata**
<a name="put_idp_metadata"></a>
> IdPExternalMetadataSettings put_idp_metadata()

Put IdP metadata

Put the external identity provider metadata as Base 64 for the Access Point

### Example

```python
import openapi_client
from openapi_client.apis.tags import identity_provider_external_metadata_api
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
    api_instance = identity_provider_external_metadata_api.IdentityProviderExternalMetadataApi(api_client)

    # example passing only optional values
    body = IdPExternalMetadataSettings(
        entity_id="entity_id_example",
        metadata="metadata_example",
        force_auth_n=True,
        allow_unencrypted=True,
        encryption_certificate_type="encryption_certificate_type_example",
        certificate_chain_and_key_wrapper=CertificateChainAndKeyWrapper(
            private_key_pem="private_key_pem_example",
            cert_chain_pem="cert_chain_pem_example",
        ),
    )
    try:
        # Put IdP metadata
        api_response = api_instance.put_idp_metadata(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IdentityProviderExternalMetadataApi->put_idp_metadata: %s\n" % e)
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
[**IdPExternalMetadataSettings**](../../models/IdPExternalMetadataSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#put_idp_metadata.ApiResponseFor200) | successful operation

#### put_idp_metadata.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**IdPExternalMetadataSettings**](../../models/IdPExternalMetadataSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

