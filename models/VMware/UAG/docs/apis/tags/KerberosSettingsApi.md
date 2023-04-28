<a name="__pageTop"></a>
# openapi_client.apis.tags.kerberos_settings_api.KerberosSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_kcd_realm**](#add_kcd_realm) | **post** /v1/config/kerberos/realm | Add a realm to krb5.conf file
[**delete_realm_settings**](#delete_realm_settings) | **delete** /v1/config/kerberos/realm/{realmName} | Delete a realm
[**get_all_principal_names_configured**](#get_all_principal_names_configured) | **get** /v1/config/kerberos/keytab | Get all keyTab principals configured
[**get_all_realms_configured**](#get_all_realms_configured) | **get** /v1/config/kerberos/realm | Get all realms configured.
[**get_key_tab_setting**](#get_key_tab_setting) | **get** /v1/config/kerberos/keytab/{principalName} | Get all keyTab principals configured
[**get_realm_settings**](#get_realm_settings) | **get** /v1/config/kerberos/realm/{realmName} | Get all realms configured.
[**update_kcd_realm**](#update_kcd_realm) | **put** /v1/config/kerberos/realm | Update a realm to krb5.conf file
[**upload_key_tab**](#upload_key_tab) | **put** /v1/config/kerberos/keytab | Upload the keytab file along with optional principal name

# **add_kcd_realm**
<a name="add_kcd_realm"></a>
> KerberosRealmSettings add_kcd_realm()

Add a realm to krb5.conf file

Provide a realm with atleast 1 KDC server host in the list

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from openapi_client.model.kerberos_realm_settings import KerberosRealmSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example passing only optional values
    body = KerberosRealmSettings(
        name="uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr",
        kdc_host_name_list=[
            "kdc_host_name_list_example"
        ],
        kdc_timeout=1,
        no_of_wrps_using_this_realm=1,
    )
    try:
        # Add a realm to krb5.conf file
        api_response = api_instance.add_kcd_realm(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->add_kcd_realm: %s\n" % e)
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
[**KerberosRealmSettings**](../../models/KerberosRealmSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#add_kcd_realm.ApiResponseFor200) | successful operation

#### add_kcd_realm.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**KerberosRealmSettings**](../../models/KerberosRealmSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_realm_settings**
<a name="delete_realm_settings"></a>
> KerberosRealmSettings delete_realm_settings(realm_name)

Delete a realm

Delete a realm configured for Kerberos Constrained Delegation

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from openapi_client.model.kerberos_realm_settings import KerberosRealmSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'realmName': "realmName_example",
    }
    try:
        # Delete a realm
        api_response = api_instance.delete_realm_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->delete_realm_settings: %s\n" % e)
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
realmName | RealmNameSchema | | 

# RealmNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#delete_realm_settings.ApiResponseFor200) | successful operation

#### delete_realm_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**KerberosRealmSettings**](../../models/KerberosRealmSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_principal_names_configured**
<a name="get_all_principal_names_configured"></a>
> [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}] get_all_principal_names_configured()

Get all keyTab principals configured

Get all keyTab principals configured.

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all keyTab principals configured
        api_response = api_instance.get_all_principal_names_configured()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->get_all_principal_names_configured: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_principal_names_configured.ApiResponseFor200) | successful operation

#### get_all_principal_names_configured.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  |  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[items](#items) | dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

# items

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_realms_configured**
<a name="get_all_realms_configured"></a>
> KerberosRealmSettingsList get_all_realms_configured()

Get all realms configured.

Get all realms configured for Kerberos Constrained Delegation

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from openapi_client.model.kerberos_realm_settings_list import KerberosRealmSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all realms configured.
        api_response = api_instance.get_all_realms_configured()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->get_all_realms_configured: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_realms_configured.ApiResponseFor200) | successful operation

#### get_all_realms_configured.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**KerberosRealmSettingsList**](../../models/KerberosRealmSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_key_tab_setting**
<a name="get_key_tab_setting"></a>
> KerberosKeyTabSettings get_key_tab_setting(principal_name)

Get all keyTab principals configured

Get all keyTab principals configured.

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from openapi_client.model.kerberos_key_tab_settings import KerberosKeyTabSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'principalName': "principalName_example",
    }
    try:
        # Get all keyTab principals configured
        api_response = api_instance.get_key_tab_setting(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->get_key_tab_setting: %s\n" % e)
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
principalName | PrincipalNameSchema | | 

# PrincipalNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_key_tab_setting.ApiResponseFor200) | successful operation

#### get_key_tab_setting.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**KerberosKeyTabSettings**](../../models/KerberosKeyTabSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_realm_settings**
<a name="get_realm_settings"></a>
> KerberosRealmSettings get_realm_settings(realm_name)

Get all realms configured.

Get all realms configured for Kerberos Constrained Delegation

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from openapi_client.model.kerberos_realm_settings import KerberosRealmSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'realmName': "realmName_example",
    }
    try:
        # Get all realms configured.
        api_response = api_instance.get_realm_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->get_realm_settings: %s\n" % e)
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
realmName | RealmNameSchema | | 

# RealmNameSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_realm_settings.ApiResponseFor200) | successful operation

#### get_realm_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**KerberosRealmSettings**](../../models/KerberosRealmSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_kcd_realm**
<a name="update_kcd_realm"></a>
> KerberosRealmSettings update_kcd_realm()

Update a realm to krb5.conf file

Provide an existing realm with atleast 1 KDC server host in the list

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from openapi_client.model.kerberos_realm_settings import KerberosRealmSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example passing only optional values
    body = KerberosRealmSettings(
        name="uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr",
        kdc_host_name_list=[
            "kdc_host_name_list_example"
        ],
        kdc_timeout=1,
        no_of_wrps_using_this_realm=1,
    )
    try:
        # Update a realm to krb5.conf file
        api_response = api_instance.update_kcd_realm(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->update_kcd_realm: %s\n" % e)
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
[**KerberosRealmSettings**](../../models/KerberosRealmSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#update_kcd_realm.ApiResponseFor200) | successful operation

#### update_kcd_realm.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**KerberosRealmSettings**](../../models/KerberosRealmSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **upload_key_tab**
<a name="upload_key_tab"></a>
> KerberosKeyTabSettings upload_key_tab()

Upload the keytab file along with optional principal name

KeyTab file input to the API should be in Base 64 encoded format.the first principal name in the keyTab shall be set as default principal nameassociated with the uploaded keyTab if the princiapl name is not provided while calling API

### Example

```python
import openapi_client
from openapi_client.apis.tags import kerberos_settings_api
from openapi_client.model.kerberos_key_tab_settings import KerberosKeyTabSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kerberos_settings_api.KerberosSettingsApi(api_client)

    # example passing only optional values
    body = KerberosKeyTabSettings(
        principal_name="principal_name_example",
        key_tab="key_tab_example",
        key_tab_file_path="key_tab_file_path_example",
        realm="realm_example",
    )
    try:
        # Upload the keytab file along with optional principal name
        api_response = api_instance.upload_key_tab(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling KerberosSettingsApi->upload_key_tab: %s\n" % e)
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
[**KerberosKeyTabSettings**](../../models/KerberosKeyTabSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#upload_key_tab.ApiResponseFor200) | successful operation

#### upload_key_tab.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**KerberosKeyTabSettings**](../../models/KerberosKeyTabSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

