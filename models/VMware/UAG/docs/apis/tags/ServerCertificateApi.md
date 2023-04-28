<a name="__pageTop"></a>
# openapi_client.apis.tags.server_certificate_api.ServerCertificateApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_ssl_certificate**](#get_ssl_certificate) | **get** /v1/config/certs/ssl | Get server certificate
[**get_ssl_certificate1**](#get_ssl_certificate1) | **get** /v1/config/certs/ssl/{entity} | Get server certificate
[**update_ssl_certificate**](#update_ssl_certificate) | **put** /v1/config/certs/ssl/{entity} | Update server certificate
[**update_ssl_certificate1**](#update_ssl_certificate1) | **put** /v1/config/certs/ssl | Update server certificate
[**update_ssl_certificate_with_pfx**](#update_ssl_certificate_with_pfx) | **put** /v1/config/certs/ssl/pfx/{entity} | Update server certificate with pfx
[**update_ssl_certificate_with_pfx1**](#update_ssl_certificate_with_pfx1) | **put** /v1/config/certs/ssl/pfx | Update server certificate with pfx

# **get_ssl_certificate**
<a name="get_ssl_certificate"></a>
> get_ssl_certificate()

Get server certificate

Gets the SSL certificate being used by the Access Point HTTPS Proxy and the BLAST Secure Gateway.

### Example

```python
import openapi_client
from openapi_client.apis.tags import server_certificate_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = server_certificate_api.ServerCertificateApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get server certificate
        api_response = api_instance.get_ssl_certificate()
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->get_ssl_certificate: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#get_ssl_certificate.ApiResponseForDefault) | successful operation

#### get_ssl_certificate.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_ssl_certificate1**
<a name="get_ssl_certificate1"></a>
> get_ssl_certificate1()

Get server certificate

Gets the SSL certificate used by the Access Point HTTPS Proxy, the PCoIP and BLAST Secure Gateway OR by the admin interface on 9443

### Example

```python
import openapi_client
from openapi_client.apis.tags import server_certificate_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = server_certificate_api.ServerCertificateApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'entity': "end_user",
    }
    try:
        # Get server certificate
        api_response = api_instance.get_ssl_certificate1(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->get_ssl_certificate1: %s\n" % e)
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
entity | EntitySchema | | 

# EntitySchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["end_user", "admin", ] if omitted the server will use the default value of "end_user"

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#get_ssl_certificate1.ApiResponseForDefault) | successful operation

#### get_ssl_certificate1.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_ssl_certificate**
<a name="update_ssl_certificate"></a>
> update_ssl_certificate()

Update server certificate

Updates the SSL certificate to use for the Access Point HTTPS Proxy, the PCoIP and BLAST Secure Gateway OR for the admin interface on 9443 SSL certificates should include the full chain of authority and the private key associated with the certificate.

### Example

```python
import openapi_client
from openapi_client.apis.tags import server_certificate_api
from openapi_client.model.certificate_chain_and_key_wrapper import CertificateChainAndKeyWrapper
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = server_certificate_api.ServerCertificateApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'entity': "end_user",
    }
    try:
        # Update server certificate
        api_response = api_instance.update_ssl_certificate(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->update_ssl_certificate: %s\n" % e)

    # example passing only optional values
    path_params = {
        'entity': "end_user",
    }
    body = CertificateChainAndKeyWrapper(
        private_key_pem="private_key_pem_example",
        cert_chain_pem="cert_chain_pem_example",
    )
    try:
        # Update server certificate
        api_response = api_instance.update_ssl_certificate(
            path_params=path_params,
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->update_ssl_certificate: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
path_params | RequestPathParams | |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**CertificateChainAndKeyWrapper**](../../models/CertificateChainAndKeyWrapper.md) |  | 


### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
entity | EntitySchema | | 

# EntitySchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["end_user", "admin", ] if omitted the server will use the default value of "end_user"

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#update_ssl_certificate.ApiResponseForDefault) | successful operation

#### update_ssl_certificate.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_ssl_certificate1**
<a name="update_ssl_certificate1"></a>
> update_ssl_certificate1()

Update server certificate

Updates the SSL certificate to use for the Access Point HTTPS Proxy and the BLAST Secure Gateway. SSL certificates should include the full chain of authority and the private key associated with the certificate.

### Example

```python
import openapi_client
from openapi_client.apis.tags import server_certificate_api
from openapi_client.model.certificate_chain_and_key_wrapper import CertificateChainAndKeyWrapper
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = server_certificate_api.ServerCertificateApi(api_client)

    # example passing only optional values
    body = CertificateChainAndKeyWrapper(
        private_key_pem="private_key_pem_example",
        cert_chain_pem="cert_chain_pem_example",
    )
    try:
        # Update server certificate
        api_response = api_instance.update_ssl_certificate1(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->update_ssl_certificate1: %s\n" % e)
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
[**CertificateChainAndKeyWrapper**](../../models/CertificateChainAndKeyWrapper.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#update_ssl_certificate1.ApiResponseForDefault) | successful operation

#### update_ssl_certificate1.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_ssl_certificate_with_pfx**
<a name="update_ssl_certificate_with_pfx"></a>
> update_ssl_certificate_with_pfx()

Update server certificate with pfx

Updates the SSL certificate to use for the Access Point HTTPS Proxy, the PCoIP and BLAST Secure Gateway OR for the admin interface on 9443 SSL certificates should include the full chain of authority and the private key associated with the certificate.

### Example

```python
import openapi_client
from openapi_client.apis.tags import server_certificate_api
from openapi_client.model.pfx_cert_store_wrapper import PfxCertStoreWrapper
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = server_certificate_api.ServerCertificateApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'entity': "end_user",
    }
    try:
        # Update server certificate with pfx
        api_response = api_instance.update_ssl_certificate_with_pfx(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->update_ssl_certificate_with_pfx: %s\n" % e)

    # example passing only optional values
    path_params = {
        'entity': "end_user",
    }
    body = PfxCertStoreWrapper(
        pfx_keystore="pfx_keystore_example",
        password="password_example",
        alias="alias_example",
    )
    try:
        # Update server certificate with pfx
        api_response = api_instance.update_ssl_certificate_with_pfx(
            path_params=path_params,
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->update_ssl_certificate_with_pfx: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
path_params | RequestPathParams | |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**PfxCertStoreWrapper**](../../models/PfxCertStoreWrapper.md) |  | 


### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
entity | EntitySchema | | 

# EntitySchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["end_user", "admin", ] if omitted the server will use the default value of "end_user"

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#update_ssl_certificate_with_pfx.ApiResponseForDefault) | successful operation

#### update_ssl_certificate_with_pfx.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_ssl_certificate_with_pfx1**
<a name="update_ssl_certificate_with_pfx1"></a>
> update_ssl_certificate_with_pfx1()

Update server certificate with pfx

Updates the SSL certificate to use for the Access Point HTTPS Proxy and the BLAST Secure Gateway. SSL certificates should include the full chain of authority and the private key associated with the certificate.

### Example

```python
import openapi_client
from openapi_client.apis.tags import server_certificate_api
from openapi_client.model.pfx_cert_store_wrapper import PfxCertStoreWrapper
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = server_certificate_api.ServerCertificateApi(api_client)

    # example passing only optional values
    body = PfxCertStoreWrapper(
        pfx_keystore="pfx_keystore_example",
        password="password_example",
        alias="alias_example",
    )
    try:
        # Update server certificate with pfx
        api_response = api_instance.update_ssl_certificate_with_pfx1(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling ServerCertificateApi->update_ssl_certificate_with_pfx1: %s\n" % e)
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
[**PfxCertStoreWrapper**](../../models/PfxCertStoreWrapper.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#update_ssl_certificate_with_pfx1.ApiResponseForDefault) | successful operation

#### update_ssl_certificate_with_pfx1.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

