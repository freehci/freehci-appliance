<a name="__pageTop"></a>
# openapi_client.apis.tags.auth_method_settings_api.AuthMethodSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_uploaded_ocsp_certificate**](#delete_uploaded_ocsp_certificate) | **delete** /v1/config/authmethod/ocsp | Delete uploaded OCSP responder Certificate.
[**get_all_auth_method_settings**](#get_all_auth_method_settings) | **get** /v1/config/authmethod | Get all authentication method settings
[**get_all_uploaded_ocsp_certificates**](#get_all_uploaded_ocsp_certificates) | **get** /v1/config/authmethod/ocsp/fileNames | Get all uploaded OCSP certificate
[**get_auth_method_settings**](#get_auth_method_settings) | **get** /v1/config/authmethod/{name} | Get authentication method settings
[**get_auth_method_settings_certificate_auth**](#get_auth_method_settings_certificate_auth) | **get** /v1/config/authmethod/certificate-auth | Get authentication method settings for the certificate-auth method
[**get_auth_method_settings_radius_auth**](#get_auth_method_settings_radius_auth) | **get** /v1/config/authmethod/radius-auth | Get authentication method settings for the radius-auth method
[**get_auth_method_settings_secur_id_idp**](#get_auth_method_settings_secur_id_idp) | **get** /v1/config/authmethod/securid-auth | Get authentication method settings for the securid-auth method
[**put_auth_method_settings_certificate_auth**](#put_auth_method_settings_certificate_auth) | **put** /v1/config/authmethod/certificate-auth | Update authentication method settings for the certificate-auth method
[**put_auth_method_settings_radius_auth**](#put_auth_method_settings_radius_auth) | **put** /v1/config/authmethod/radius-auth | Update authentication method settings for the radius-auth method
[**put_auth_method_settings_secur_id_idp**](#put_auth_method_settings_secur_id_idp) | **put** /v1/config/authmethod/securid-auth | Update authentication method settings for the securid-auth method
[**reset_auth_method_settings**](#reset_auth_method_settings) | **put** /v1/config/authmethod/reset/{name} | Reset required auth method settings
[**update_auth_method_settings**](#update_auth_method_settings) | **put** /v1/config/authmethod/{name} | Update authentication method settings
[**upload_ocsp_certificate**](#upload_ocsp_certificate) | **put** /v1/config/authmethod/ocsp/certificate | Upload OCSP certificate

# **delete_uploaded_ocsp_certificate**
<a name="delete_uploaded_ocsp_certificate"></a>
> delete_uploaded_ocsp_certificate()

Delete uploaded OCSP responder Certificate.

This operation is valid only for certificate authentication

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only optional values
    body = "body_example"
    try:
        # Delete uploaded OCSP responder Certificate.
        api_response = api_instance.delete_uploaded_ocsp_certificate(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->delete_uploaded_ocsp_certificate: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBody, Unset] | optional, default is unset |
content_type | str | optional, default is '*/*' | Selects the schema and serialization of the request body
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBody

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#delete_uploaded_ocsp_certificate.ApiResponseForDefault) | successful operation

#### delete_uploaded_ocsp_certificate.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_auth_method_settings**
<a name="get_all_auth_method_settings"></a>
> AuthMethodSettingsList get_all_auth_method_settings()

Get all authentication method settings

Get all the authentication method settings.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from openapi_client.model.auth_method_settings_list import AuthMethodSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all authentication method settings
        api_response = api_instance.get_all_auth_method_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->get_all_auth_method_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_auth_method_settings.ApiResponseFor200) | successful operation

#### get_all_auth_method_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**AuthMethodSettingsList**](../../models/AuthMethodSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_uploaded_ocsp_certificates**
<a name="get_all_uploaded_ocsp_certificates"></a>
> get_all_uploaded_ocsp_certificates()

Get all uploaded OCSP certificate

This operation is valid only for certificate authentication.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all uploaded OCSP certificate
        api_response = api_instance.get_all_uploaded_ocsp_certificates()
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->get_all_uploaded_ocsp_certificates: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#get_all_uploaded_ocsp_certificates.ApiResponseForDefault) | successful operation

#### get_all_uploaded_ocsp_certificates.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_auth_method_settings**
<a name="get_auth_method_settings"></a>
> {str: (str,)} get_auth_method_settings(name)

Get authentication method settings

Gets authentication method settings for the specified authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Get authentication method settings
        api_response = api_instance.get_auth_method_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->get_auth_method_settings: %s\n" % e)
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

# NameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_auth_method_settings.ApiResponseFor200) | successful operation

#### get_auth_method_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**any_string_name** | str,  | str,  | any string name can be used but the value must be the correct type | [optional] 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_auth_method_settings_certificate_auth**
<a name="get_auth_method_settings_certificate_auth"></a>
> CertificateAuthMethodSettings get_auth_method_settings_certificate_auth()

Get authentication method settings for the certificate-auth method

Gets authentication method settings for the certificate-auth authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from openapi_client.model.certificate_auth_method_settings import CertificateAuthMethodSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get authentication method settings for the certificate-auth method
        api_response = api_instance.get_auth_method_settings_certificate_auth()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->get_auth_method_settings_certificate_auth: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_auth_method_settings_certificate_auth.ApiResponseFor200) | successful operation

#### get_auth_method_settings_certificate_auth.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**CertificateAuthMethodSettings**](../../models/CertificateAuthMethodSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_auth_method_settings_radius_auth**
<a name="get_auth_method_settings_radius_auth"></a>
> RadiusAuthMethodSettings get_auth_method_settings_radius_auth()

Get authentication method settings for the radius-auth method

Gets authentication method settings for the radius-auth authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from openapi_client.model.radius_auth_method_settings import RadiusAuthMethodSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get authentication method settings for the radius-auth method
        api_response = api_instance.get_auth_method_settings_radius_auth()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->get_auth_method_settings_radius_auth: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_auth_method_settings_radius_auth.ApiResponseFor200) | successful operation

#### get_auth_method_settings_radius_auth.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**RadiusAuthMethodSettings**](../../models/RadiusAuthMethodSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_auth_method_settings_secur_id_idp**
<a name="get_auth_method_settings_secur_id_idp"></a>
> SecurIDIdpMethodSettings get_auth_method_settings_secur_id_idp()

Get authentication method settings for the securid-auth method

Gets authentication method settings for the securid-auth authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from openapi_client.model.secur_id_idp_method_settings import SecurIDIdpMethodSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get authentication method settings for the securid-auth method
        api_response = api_instance.get_auth_method_settings_secur_id_idp()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->get_auth_method_settings_secur_id_idp: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_auth_method_settings_secur_id_idp.ApiResponseFor200) | successful operation

#### get_auth_method_settings_secur_id_idp.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SecurIDIdpMethodSettings**](../../models/SecurIDIdpMethodSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **put_auth_method_settings_certificate_auth**
<a name="put_auth_method_settings_certificate_auth"></a>
> CertificateAuthMethodSettings put_auth_method_settings_certificate_auth()

Update authentication method settings for the certificate-auth method

Updates authentication method settings for the certificate-auth authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from openapi_client.model.certificate_auth_method_settings import CertificateAuthMethodSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only optional values
    body = CertificateAuthMethodSettings(
        name="name_example",
        class_name="class_name_example",
        display_name="display_name_example",
        jar_file="jar_file_example",
        auth_method="auth_method_example",
        version_num="version_num_example",
        enabled=False,
        ca_certificates="A list of trusted CA certificates in PEM format.",
        user_id_source="Select the search order for locating the user identifier within the certificate. upn: UserPrincipalName value from the Subject Alternative Name; email: Email address from the Subject Alternative Name; subject: UID value from the Subject",
        validate_upn=False,
        request_timeout="Timeout in seconds to wait for a response.  A value of zero will wait indefinitely.",
        certificate_policies="Object Identifier (OID) list that is accepted in the Certificate Policies extension",
        enable_cert_revocation=False,
        enable_cert_crl=False,
        crl_location="CRL location to use for revocation check (e.g. http://crlurl.crl or file:///crlFile.crl)",
        enable_ocsp=True,
        enable_ocspcrl_failover=False,
        send_ocsp_nonce=False,
        ocsp_url="OCSP URL to use for revocation check (e.g. http://ocspurl.com).",
        ocsp_url_source="Source for OCSP URL: configuration, certificate or both",
        enable_consent_form=False,
        consent_form="The content of the consent form to be displayed",
    )
    try:
        # Update authentication method settings for the certificate-auth method
        api_response = api_instance.put_auth_method_settings_certificate_auth(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->put_auth_method_settings_certificate_auth: %s\n" % e)
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
[**CertificateAuthMethodSettings**](../../models/CertificateAuthMethodSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#put_auth_method_settings_certificate_auth.ApiResponseFor200) | successful operation

#### put_auth_method_settings_certificate_auth.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**CertificateAuthMethodSettings**](../../models/CertificateAuthMethodSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **put_auth_method_settings_radius_auth**
<a name="put_auth_method_settings_radius_auth"></a>
> RadiusAuthMethodSettings put_auth_method_settings_radius_auth()

Update authentication method settings for the radius-auth method

Updates authentication method settings for the radius-auth authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from openapi_client.model.radius_auth_method_settings import RadiusAuthMethodSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only optional values
    body = RadiusAuthMethodSettings(
        name="name_example",
        class_name="class_name_example",
        display_name="display_name_example",
        jar_file="jar_file_example",
        auth_method="auth_method_example",
        version_num="version_num_example",
        enabled=True,
        num_iterations="Number of retries before authentication fails",
        radius_display_hint="radius_display_hint_example",
        radius_custom_passphrase_hint="radius_custom_passphrase_hint_example",
        direct_auth_chained_username=True,
        num_attempts="num_attempts_example",
        server_timeout="server_timeout_example",
        host_name="host_name_example",
        auth_port="auth_port_example",
        accounting_port="accounting_port_example",
        auth_type="PAP",
        shared_secret="shared_secret_example",
        realm_prefix="realm_prefix_example",
        realm_suffix="realm_suffix_example",
        enable_basic_mschapv2_validation_1=True,
        enabled_aux=True,
        num_attempts_2="num_attempts_2_example",
        server_timeout_2="server_timeout_2_example",
        host_name_2="host_name_2_example",
        auth_port_2="auth_port_2_example",
        accounting_port_2="accounting_port_2_example",
        auth_type_2="PAP",
        shared_secret_2="shared_secret_2_example",
        name_id_suffix=dict(),
        realm_prefix_2="realm_prefix_2_example",
        realm_suffix_2="realm_suffix_2_example",
        enable_basic_mschapv2_validation_2=True,
        show_domain_if_user_input_available=False,
    )
    try:
        # Update authentication method settings for the radius-auth method
        api_response = api_instance.put_auth_method_settings_radius_auth(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->put_auth_method_settings_radius_auth: %s\n" % e)
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
[**RadiusAuthMethodSettings**](../../models/RadiusAuthMethodSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#put_auth_method_settings_radius_auth.ApiResponseFor200) | successful operation

#### put_auth_method_settings_radius_auth.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**RadiusAuthMethodSettings**](../../models/RadiusAuthMethodSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **put_auth_method_settings_secur_id_idp**
<a name="put_auth_method_settings_secur_id_idp"></a>
> SecurIDIdpMethodSettings put_auth_method_settings_secur_id_idp()

Update authentication method settings for the securid-auth method

Updates authentication method settings for the securid-auth authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from openapi_client.model.secur_id_idp_method_settings import SecurIDIdpMethodSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only optional values
    body = SecurIDIdpMethodSettings(
        name="name_example",
        class_name="class_name_example",
        display_name="display_name_example",
        jar_file="jar_file_example",
        auth_method="auth_method_example",
        version_num="version_num_example",
        enabled=False,
        num_iterations_rest="Number of retries before authentication fails.",
        server_hostname_rest="Enter the SecurID hostname or IP Address",
        server_port_rest="SecurID Port for HTTP Requests",
        hostname="Enter the host name of connector instance without scheme(HTTP/HTTPS)",
        access_key_rest="Enter Access Key",
        certificate_rest="Enter Ssl Certificates",
        authentication_timeout_rest="Enter Authentication Timeout In Seconds",
    )
    try:
        # Update authentication method settings for the securid-auth method
        api_response = api_instance.put_auth_method_settings_secur_id_idp(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->put_auth_method_settings_secur_id_idp: %s\n" % e)
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
[**SecurIDIdpMethodSettings**](../../models/SecurIDIdpMethodSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#put_auth_method_settings_secur_id_idp.ApiResponseFor200) | successful operation

#### put_auth_method_settings_secur_id_idp.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SecurIDIdpMethodSettings**](../../models/SecurIDIdpMethodSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **reset_auth_method_settings**
<a name="reset_auth_method_settings"></a>
> reset_auth_method_settings(name)

Reset required auth method settings

resets the auth adapter settings.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Reset required auth method settings
        api_response = api_instance.reset_auth_method_settings(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->reset_auth_method_settings: %s\n" % e)
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
name | NameSchema | | 

# NameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#reset_auth_method_settings.ApiResponseForDefault) | successful operation

#### reset_auth_method_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_auth_method_settings**
<a name="update_auth_method_settings"></a>
> {str: (str,)} update_auth_method_settings(name)

Update authentication method settings

Endpoint for updating the settings for an authentication method.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Update authentication method settings
        api_response = api_instance.update_auth_method_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->update_auth_method_settings: %s\n" % e)

    # example passing only optional values
    path_params = {
        'name': "name_example",
    }
    body = dict(
        "key": "key_example",
    )
    try:
        # Update authentication method settings
        api_response = api_instance.update_auth_method_settings(
            path_params=path_params,
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->update_auth_method_settings: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, Unset] | optional, default is unset |
path_params | RequestPathParams | |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**any_string_name** | str,  | str,  | any string name can be used but the value must be the correct type | [optional] 

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
name | NameSchema | | 

# NameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#update_auth_method_settings.ApiResponseFor200) | successful operation

#### update_auth_method_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**any_string_name** | str,  | str,  | any string name can be used but the value must be the correct type | [optional] 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **upload_ocsp_certificate**
<a name="upload_ocsp_certificate"></a>
> upload_ocsp_certificate()

Upload OCSP certificate

This operation is valid only for certificate authentication.

### Example

```python
import openapi_client
from openapi_client.apis.tags import auth_method_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auth_method_settings_api.AuthMethodSettingsApi(api_client)

    # example passing only optional values
    body = "body_example"
    try:
        # Upload OCSP certificate
        api_response = api_instance.upload_ocsp_certificate(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling AuthMethodSettingsApi->upload_ocsp_certificate: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBody, Unset] | optional, default is unset |
content_type | str | optional, default is '*/*' | Selects the schema and serialization of the request body
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

# SchemaForRequestBody

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#upload_ocsp_certificate.ApiResponseForDefault) | successful operation

#### upload_ocsp_certificate.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

