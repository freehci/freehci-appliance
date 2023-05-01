<a name="__pageTop"></a>
# openapi_client.apis.tags.identity_provider_metadata_api.IdentityProviderMetadataApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**generate_id_p_metadata**](#generate_id_p_metadata) | **post** /v1/config/idp-metadata | Set IdP metadata
[**get_id_p_metadata2**](#get_id_p_metadata2) | **get** /v1/config/idp-metadata/{hostName} | Get IdP metadata
[**get_id_p_metadata3**](#get_id_p_metadata3) | **get** /v1/config/idp-metadata | Get IdP metadata

# **generate_id_p_metadata**
<a name="generate_id_p_metadata"></a>
> IdpMediaType generate_id_p_metadata()

Set IdP metadata

Set the identity provider metadata XML for the Access Point. The IDP metadata can only be set once. The signing certificate is generated automatically if omitted from the request (use {} as the Javascript body of the request).

### Example

```python
import openapi_client
from openapi_client.apis.tags import identity_provider_metadata_api
from openapi_client.model.certificate_chain_and_key_wrapper import CertificateChainAndKeyWrapper
from openapi_client.model.idp_media_type import IdpMediaType
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_provider_metadata_api.IdentityProviderMetadataApi(api_client)

    # example passing only optional values
    body = CertificateChainAndKeyWrapper(
        private_key_pem="private_key_pem_example",
        cert_chain_pem="cert_chain_pem_example",
    )
    try:
        # Set IdP metadata
        api_response = api_instance.generate_id_p_metadata(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IdentityProviderMetadataApi->generate_id_p_metadata: %s\n" % e)
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
[**CertificateChainAndKeyWrapper**](../../models/CertificateChainAndKeyWrapper.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#generate_id_p_metadata.ApiResponseFor200) | successful operation

#### generate_id_p_metadata.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**IdpMediaType**](../../models/IdpMediaType.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_id_p_metadata2**
<a name="get_id_p_metadata2"></a>
> str get_id_p_metadata2(host_name)

Get IdP metadata

Get the identity provider metadata XML for the Access Point with external host name. For Web Reverse Proxy use this API as the login URL in mata data must be an accessible URL.

### Example

```python
import openapi_client
from openapi_client.apis.tags import identity_provider_metadata_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_provider_metadata_api.IdentityProviderMetadataApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'hostName': "hostName_example",
    }
    try:
        # Get IdP metadata
        api_response = api_instance.get_id_p_metadata2(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IdentityProviderMetadataApi->get_id_p_metadata2: %s\n" % e)
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
hostName | HostNameSchema | | 

# HostNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_id_p_metadata2.ApiResponseFor200) | successful operation

#### get_id_p_metadata2.ApiResponseFor200
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

# **get_id_p_metadata3**
<a name="get_id_p_metadata3"></a>
> str get_id_p_metadata3()

Get IdP metadata

Get the identity provider metadata XML for the Access Point

### Example

```python
import openapi_client
from openapi_client.apis.tags import identity_provider_metadata_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_provider_metadata_api.IdentityProviderMetadataApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get IdP metadata
        api_response = api_instance.get_id_p_metadata3()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling IdentityProviderMetadataApi->get_id_p_metadata3: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_id_p_metadata3.ApiResponseFor200) | successful operation

#### get_id_p_metadata3.ApiResponseFor200
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

