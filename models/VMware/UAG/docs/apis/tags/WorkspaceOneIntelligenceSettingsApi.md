<a name="__pageTop"></a>
# openapi_client.apis.tags.workspace_one_intelligence_settings_api.WorkspaceOneIntelligenceSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_ws1_intelligence_settings**](#create_ws1_intelligence_settings) | **post** /v1/config/ws1intelligence | Add Workspace ONE Intelligence settings
[**delete_ws1_intelligence_settings**](#delete_ws1_intelligence_settings) | **delete** /v1/config/ws1intelligence/{name} | Delete Workspace ONE Intelligence Settings
[**get_all_ws1_intelligence_settings**](#get_all_ws1_intelligence_settings) | **get** /v1/config/ws1intelligence | Get all Workspace ONE Intelligence Settings
[**get_ws1_intelligence_settings**](#get_ws1_intelligence_settings) | **get** /v1/config/ws1intelligence/{name} | Get Workspace ONE Intelligence settings
[**update_ws1_intelligence_settings**](#update_ws1_intelligence_settings) | **put** /v1/config/ws1intelligence | Update Workspace ONE Intelligence settings

# **create_ws1_intelligence_settings**
<a name="create_ws1_intelligence_settings"></a>
> create_ws1_intelligence_settings()

Add Workspace ONE Intelligence settings

Add Workspace ONE Intelligence settings for the UAG 

### Example

```python
import openapi_client
from openapi_client.apis.tags import workspace_one_intelligence_settings_api
from openapi_client.model.workspace_one_intelligence_settings import WorkspaceOneIntelligenceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace_one_intelligence_settings_api.WorkspaceOneIntelligenceSettingsApi(api_client)

    # example passing only optional values
    body = WorkspaceOneIntelligenceSettings(
        name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
        encoded_credentials_file_content="encoded_credentials_file_content_example",
        url_thumbprints="B00829:cc FFCfEe50C3Dc:c8 3DD7 F7678895 ce 1Cb7CB 8Dac EA:2B7fD63d:FF95 Be894E,                                                          sha384=E1 0D:c8:CFD5 bF486347F0D5 9aC71BE262:B58A fc D5:DA:7b:9A:60 f27f D7:c739b02297a194:C6:1509 99 28 60e5Cc:eDe3Cf1713 2cdD 6A8d3C:cd EA d3 2c 3b:9F 4A42:A0:931b31,                                                                    sha1=9f 1cB2,                                        AE 07bECA:62fAbCDF00:7470d9:8a4F 5fdCC8:A7 a59c8Af7 aC1C:E4e75538:D5:57Bdb3:AfCD:aeBA:76:9e ed0f AC:95:1535 d7 c6 2A37 47aE1748:E5:3f:bAA4Db DB81:31:f3:0aaDcC:aB:98c925AC 9cEc:D9 cA26Da BEcDEe:73ED61AC:6a 24:d3:7d4AF6dD Ad F6F3 bD 5D,                        md5=ba8e:28E5a2a2:EFBc9FeD e6bafc5e18:b6:12:39C6 72 dc1C59:bb 0a0Acc Cb2a:98 C3 ebe89ECE C8ac6d10 01dd e967:feBa 57 5a:0ceA:54 Bf 3D9A F43E:cEFB42:AC:4B 47aE52FBbD,                                                       sha384=71F0:De:AfE5:Dd b0Ce 3F:DE7f aa:76 9eBf:Ae:9C94:Bee2b2Efd9:39A4:B5:47d6 2CEE8D:CDDF BA:bfF1:7a:C8:74 4C,                                                                           sha1=7d:b924:ab0E:c7:b3 daa8:a6 1F:c589 76:D27aFE:bB2f ba79 994B88 DD:BE:e86ad9 0e:A5aC3bcc e8:7d:4eDa:Aa8dDbB354 EdCF 2008:49:48 8E6F:8FCb7B 5e7076Df:20bcceAf 55B1CA DFBFb3 bdbA 7B cE2DD09FEd bc:43:c7:d48113,                                         dE deEF:4f:1c:92AFE4 26 d4dF:30C034AF6b:F72CB12c:9B:a0:Ef:2E C2 BC4D 1a 3DF05416a4a5 DD:28,                                                            sha256=Bdf1 7f89:F2 b5F4 4d:CaF726Fe:cebaaDEE:e3:315Af5f7:eD3d d9:ee eEBB3dd8,                                                          8E:fa3f fde132c2:9185:98:da 5B:a6 55 e2:f823 A4 33D8fb56d53fe5:c4CB:8a ddfc 7f:Fdb875:DCC16362:3ECB:7884:66 EbA7a9 Db:e5:3a:3a C3 ffeFaA4C:Fea7:EB:c5:f3315F,                                                                        sha256=bd:94A822:3C:C805D9:DB f4A553 F6D9 ADD1Ab:FDFa:68B8 BA eBadFE fE69E94108 44:bA:ea 878dd2 Fc,                                c681b2eFc0,                                                                          eB2B 79 6d A430:7E:7Fec8D21:BA5C 6B973c734AE8:F35B Bd:f9F5:2Aa5 eA:dc0a 3a15d177652A50:dF:6c 5A:eC:E9D2D3:B8 16:8E 0Bd3 65,                                                                  9c 66:AD b8 dc Ad:e1Fcbe01dA0B F9:D1:af EFb3105E 78:37 4fc7 7F:7A 5202a6ccaE0eEB57:aeb576B2:9Fa597 d0 C605cc 48:fd9b7D cE783E41 bd:65:3409,                       b5 cB84:2a:AFFD eD5f2f:c7 25e7:15 cc be 6e 4c17:19Ae deA0B0:9b32 4Ab0 cf:C5:2969:BE:0AaF:A81E:66 A4 00:3B 393a918F67bD:037E:dC:0e fe:49e1D919:4A fD05 EA89b48cF7 AB16:7Beda59a CD 7b68 8Cb7,                 F8fd B06bCd6E e7 39:28 3A 9B2e9f7D40Ce08 8c8b:0ca5 21 aC,                                                 3E 3ea5 c72a C6 57:31fF4E4FFA:A3fCcc 1F2f6BA3 CDdfeB:9d fFfD:e2 7ace:1DDbABfd:bBD7 c87e 001abE5A48 4213 bA55dc:c1,                                                                                           A8FAD683 bcb3:f5:eBAae7ed2B eC2eA9:e3d660C0:29 Cd:Fda72E:B8:AF 8d:CC26:8532 26FE:29 Ca 7949cFbC 09cd fD:B5:D9 017e:9C0d fEbC09 81 fF5637:c563595D9D7E:e0D7:EC aFB9 Ab34:0c4d:cA5a:CeE7 C0BcB4 Efa7 D1:cB61,                                                   af:c5 cA:d2:0d7c6E:0233dF e4 aC BE:Da 62:e4:Cc 6327 caD7 4eC4 45 Ea 6d CA 3C:ad44BCbf f01e3E 1C 8e37 12A0 Ef2E:3d:a526 eD,                  B1:DC bC D3:dFAf:93 37:eD:6eF59C 32 F8bf:9Aa77b 15:82 fD 79 3C5F:83 aa B8 b48BD9 939A:30 4f D4:5E6c:54ae:a3 84FB4e91 aB 02:D4686eeB 3e:F3129C 1756Bd12 ce:ffDeFA Fa Ef D3 9b de 2E0E5D:7a Bf FDB6 547E 2CA3:dF 27eaBE7E:01:7A a8:54,                                             sha384=24afd2:8f:a37A92a52dE3344C:cC:E6 Fe:de:f4 8C:6C Cc:F6:5F8b,        Fc:35C2 17 CF:1b f1 f7fad5 1432Cc:b5c8:ab075475 0d d0bf:fb EdB8:3bCA40:34:B2:10dd:b67fdffEeb:5e 17:47 ED29:67 FBd8E0CA:1B:bD db eCF74C00 5742F35Ddff9 1F:C7,                                                         0eDae2a48fc4Db3d6e:bC6F4B 0C 48:9A 0dAbC5da dC:CA0834:F03a:Fc7a:38511D 2Cd4BeCd 599cfE:DafaB8 E1c5:8Add bB14 D1:2Da8:94d6a7F9:6Cd7 fDA3 d89b61:11 b1:cc:9c:F6 8a 4e b1 2943 Efba fDEB 562B4A54127DCC6eC3FB eA:bd:eA4FCDA5 5EcB 71,           sha1=0F 90a3ebAFfEDc d6 7AdBb7:cC a3 EDE9CE:89 AcEeec:F0 66:02 7EBb50 EE 7B:c75098 B0f5Dc2e 6A:C7:4DBE:F9 47:BC7d d7cA 58 B3:17f7f0:5Ed7 Ba:6bBc 2F 5C:7f:7B:65:dBC8 b9:fB:A757FE98aD EE fE:c00D 822444E8dd154804:15cD:D8eb37 5A 0BeC,                                                                      Ad:1EaB 504DF5 9D6D B1be 3B38:3d:3e:c944 53:d5,                           sha512=47 9acE 97F7:E22c28:c20B:0C081DCfEE C0de CCACa6 C8E5bd:Cc 1A:eE:40:5E 3f64:D0e4 68df:7D:bb:1B:8b1f 83:E2:47:B2:9Fbee8fED41c:c620:94AFDADdC9:e1:BA:3d5F:D9,                                                                     81ab:cFc0 fa0dd1 0d:F6:b62AE6bef98a:d1dc5d:fcAD3d e0 6102:5EdFbB345e158Ee0D4 aA8E:e2 bD57B5:0F 0Cfb:ed AE9C f0 E7 47 b19ACE:7Bfa:50E633 fB,                                                                28:D95e:95:F3fd72:Aa:C62017:64Ae:Bc 0F:3297:fc:c9 6Dea1F AB9De2b0:6D556fe3:9B1F e6cA:f0 B5 96 b4:d9:fAAe B900 6B:14 BAFBe9Ce Ed13 fc4E 3F:d617 49 9b Ea,                                                                             sha1=26C517 ca:ac32:a497 B2 cc ef 9D 1ADF 8E:64:EB9d621d:C9a3 AaC6 27a1 67Bd F6:012A af fabF:0BAB:C7FAEf0DaBEb 29 9f:3c:2ddd:BBce:4CD5:Fc F5bc 8276ee E7Ba5d4d0e:8fC2F92B 2E 65 2CE7Ba98 91b3A4 f6",
        trusted_certificates=[
            PublicKeyOrCert(
                name="name_example",
                data="data_example",
            )
        ],
        ws1_intelligence_credentials=WS1IntelligenceCredentials(
            data=WS1IntelligenceData(
                oauth_client=WS1IntelligenceOAuthClient(
                    client_id="client_id_example",
                    client_secret="client_secret_example",
                    scopes=[
                        "scopes_example"
                    ],
                    access_token_validity_secs=1,
                    refresh_token_validity_secs=1,
                    integration="integration_example",
                    source_system_id="source_system_id_example",
                    org_id="org_id_example",
,
,
                ),
                events_base_url="events_base_url_example",
                token_endpoint="token_endpoint_example",
                api_base_url="api_base_url_example",
            ),
        ),
    )
    try:
        # Add Workspace ONE Intelligence settings
        api_response = api_instance.create_ws1_intelligence_settings(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling WorkspaceOneIntelligenceSettingsApi->create_ws1_intelligence_settings: %s\n" % e)
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
[**WorkspaceOneIntelligenceSettings**](../../models/WorkspaceOneIntelligenceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#create_ws1_intelligence_settings.ApiResponseForDefault) | successful operation

#### create_ws1_intelligence_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **delete_ws1_intelligence_settings**
<a name="delete_ws1_intelligence_settings"></a>
> WS1IntelligenceSettingsList delete_ws1_intelligence_settings(name)

Delete Workspace ONE Intelligence Settings

Delete existing Workspace ONE Intelligence settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import workspace_one_intelligence_settings_api
from openapi_client.model.ws1_intelligence_settings_list import WS1IntelligenceSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace_one_intelligence_settings_api.WorkspaceOneIntelligenceSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Delete Workspace ONE Intelligence Settings
        api_response = api_instance.delete_ws1_intelligence_settings(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling WorkspaceOneIntelligenceSettingsApi->delete_ws1_intelligence_settings: %s\n" % e)
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
200 | [ApiResponseFor200](#delete_ws1_intelligence_settings.ApiResponseFor200) | successful operation

#### delete_ws1_intelligence_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**WS1IntelligenceSettingsList**](../../models/WS1IntelligenceSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_all_ws1_intelligence_settings**
<a name="get_all_ws1_intelligence_settings"></a>
> WS1IntelligenceSettingsList get_all_ws1_intelligence_settings()

Get all Workspace ONE Intelligence Settings

Get the list of all Workspace ONE Intelligence Settings

### Example

```python
import openapi_client
from openapi_client.apis.tags import workspace_one_intelligence_settings_api
from openapi_client.model.ws1_intelligence_settings_list import WS1IntelligenceSettingsList
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace_one_intelligence_settings_api.WorkspaceOneIntelligenceSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get all Workspace ONE Intelligence Settings
        api_response = api_instance.get_all_ws1_intelligence_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling WorkspaceOneIntelligenceSettingsApi->get_all_ws1_intelligence_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_all_ws1_intelligence_settings.ApiResponseFor200) | successful operation

#### get_all_ws1_intelligence_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**WS1IntelligenceSettingsList**](../../models/WS1IntelligenceSettingsList.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_ws1_intelligence_settings**
<a name="get_ws1_intelligence_settings"></a>
> get_ws1_intelligence_settings(name)

Get Workspace ONE Intelligence settings

Get Workspace ONE Intelligence settings for the UAG

### Example

```python
import openapi_client
from openapi_client.apis.tags import workspace_one_intelligence_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace_one_intelligence_settings_api.WorkspaceOneIntelligenceSettingsApi(api_client)

    # example passing only required values which don't have defaults set
    path_params = {
        'name': "name_example",
    }
    try:
        # Get Workspace ONE Intelligence settings
        api_response = api_instance.get_ws1_intelligence_settings(
            path_params=path_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling WorkspaceOneIntelligenceSettingsApi->get_ws1_intelligence_settings: %s\n" % e)
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
default | [ApiResponseForDefault](#get_ws1_intelligence_settings.ApiResponseForDefault) | successful operation

#### get_ws1_intelligence_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **update_ws1_intelligence_settings**
<a name="update_ws1_intelligence_settings"></a>
> update_ws1_intelligence_settings()

Update Workspace ONE Intelligence settings

Update Workspace ONE Intelligence settings for the UAG 

### Example

```python
import openapi_client
from openapi_client.apis.tags import workspace_one_intelligence_settings_api
from openapi_client.model.workspace_one_intelligence_settings import WorkspaceOneIntelligenceSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace_one_intelligence_settings_api.WorkspaceOneIntelligenceSettingsApi(api_client)

    # example passing only optional values
    body = WorkspaceOneIntelligenceSettings(
        name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
        encoded_credentials_file_content="encoded_credentials_file_content_example",
        url_thumbprints="B00829:cc FFCfEe50C3Dc:c8 3DD7 F7678895 ce 1Cb7CB 8Dac EA:2B7fD63d:FF95 Be894E,                                                          sha384=E1 0D:c8:CFD5 bF486347F0D5 9aC71BE262:B58A fc D5:DA:7b:9A:60 f27f D7:c739b02297a194:C6:1509 99 28 60e5Cc:eDe3Cf1713 2cdD 6A8d3C:cd EA d3 2c 3b:9F 4A42:A0:931b31,                                                                    sha1=9f 1cB2,                                        AE 07bECA:62fAbCDF00:7470d9:8a4F 5fdCC8:A7 a59c8Af7 aC1C:E4e75538:D5:57Bdb3:AfCD:aeBA:76:9e ed0f AC:95:1535 d7 c6 2A37 47aE1748:E5:3f:bAA4Db DB81:31:f3:0aaDcC:aB:98c925AC 9cEc:D9 cA26Da BEcDEe:73ED61AC:6a 24:d3:7d4AF6dD Ad F6F3 bD 5D,                        md5=ba8e:28E5a2a2:EFBc9FeD e6bafc5e18:b6:12:39C6 72 dc1C59:bb 0a0Acc Cb2a:98 C3 ebe89ECE C8ac6d10 01dd e967:feBa 57 5a:0ceA:54 Bf 3D9A F43E:cEFB42:AC:4B 47aE52FBbD,                                                       sha384=71F0:De:AfE5:Dd b0Ce 3F:DE7f aa:76 9eBf:Ae:9C94:Bee2b2Efd9:39A4:B5:47d6 2CEE8D:CDDF BA:bfF1:7a:C8:74 4C,                                                                           sha1=7d:b924:ab0E:c7:b3 daa8:a6 1F:c589 76:D27aFE:bB2f ba79 994B88 DD:BE:e86ad9 0e:A5aC3bcc e8:7d:4eDa:Aa8dDbB354 EdCF 2008:49:48 8E6F:8FCb7B 5e7076Df:20bcceAf 55B1CA DFBFb3 bdbA 7B cE2DD09FEd bc:43:c7:d48113,                                         dE deEF:4f:1c:92AFE4 26 d4dF:30C034AF6b:F72CB12c:9B:a0:Ef:2E C2 BC4D 1a 3DF05416a4a5 DD:28,                                                            sha256=Bdf1 7f89:F2 b5F4 4d:CaF726Fe:cebaaDEE:e3:315Af5f7:eD3d d9:ee eEBB3dd8,                                                          8E:fa3f fde132c2:9185:98:da 5B:a6 55 e2:f823 A4 33D8fb56d53fe5:c4CB:8a ddfc 7f:Fdb875:DCC16362:3ECB:7884:66 EbA7a9 Db:e5:3a:3a C3 ffeFaA4C:Fea7:EB:c5:f3315F,                                                                        sha256=bd:94A822:3C:C805D9:DB f4A553 F6D9 ADD1Ab:FDFa:68B8 BA eBadFE fE69E94108 44:bA:ea 878dd2 Fc,                                c681b2eFc0,                                                                          eB2B 79 6d A430:7E:7Fec8D21:BA5C 6B973c734AE8:F35B Bd:f9F5:2Aa5 eA:dc0a 3a15d177652A50:dF:6c 5A:eC:E9D2D3:B8 16:8E 0Bd3 65,                                                                  9c 66:AD b8 dc Ad:e1Fcbe01dA0B F9:D1:af EFb3105E 78:37 4fc7 7F:7A 5202a6ccaE0eEB57:aeb576B2:9Fa597 d0 C605cc 48:fd9b7D cE783E41 bd:65:3409,                       b5 cB84:2a:AFFD eD5f2f:c7 25e7:15 cc be 6e 4c17:19Ae deA0B0:9b32 4Ab0 cf:C5:2969:BE:0AaF:A81E:66 A4 00:3B 393a918F67bD:037E:dC:0e fe:49e1D919:4A fD05 EA89b48cF7 AB16:7Beda59a CD 7b68 8Cb7,                 F8fd B06bCd6E e7 39:28 3A 9B2e9f7D40Ce08 8c8b:0ca5 21 aC,                                                 3E 3ea5 c72a C6 57:31fF4E4FFA:A3fCcc 1F2f6BA3 CDdfeB:9d fFfD:e2 7ace:1DDbABfd:bBD7 c87e 001abE5A48 4213 bA55dc:c1,                                                                                           A8FAD683 bcb3:f5:eBAae7ed2B eC2eA9:e3d660C0:29 Cd:Fda72E:B8:AF 8d:CC26:8532 26FE:29 Ca 7949cFbC 09cd fD:B5:D9 017e:9C0d fEbC09 81 fF5637:c563595D9D7E:e0D7:EC aFB9 Ab34:0c4d:cA5a:CeE7 C0BcB4 Efa7 D1:cB61,                                                   af:c5 cA:d2:0d7c6E:0233dF e4 aC BE:Da 62:e4:Cc 6327 caD7 4eC4 45 Ea 6d CA 3C:ad44BCbf f01e3E 1C 8e37 12A0 Ef2E:3d:a526 eD,                  B1:DC bC D3:dFAf:93 37:eD:6eF59C 32 F8bf:9Aa77b 15:82 fD 79 3C5F:83 aa B8 b48BD9 939A:30 4f D4:5E6c:54ae:a3 84FB4e91 aB 02:D4686eeB 3e:F3129C 1756Bd12 ce:ffDeFA Fa Ef D3 9b de 2E0E5D:7a Bf FDB6 547E 2CA3:dF 27eaBE7E:01:7A a8:54,                                             sha384=24afd2:8f:a37A92a52dE3344C:cC:E6 Fe:de:f4 8C:6C Cc:F6:5F8b,        Fc:35C2 17 CF:1b f1 f7fad5 1432Cc:b5c8:ab075475 0d d0bf:fb EdB8:3bCA40:34:B2:10dd:b67fdffEeb:5e 17:47 ED29:67 FBd8E0CA:1B:bD db eCF74C00 5742F35Ddff9 1F:C7,                                                         0eDae2a48fc4Db3d6e:bC6F4B 0C 48:9A 0dAbC5da dC:CA0834:F03a:Fc7a:38511D 2Cd4BeCd 599cfE:DafaB8 E1c5:8Add bB14 D1:2Da8:94d6a7F9:6Cd7 fDA3 d89b61:11 b1:cc:9c:F6 8a 4e b1 2943 Efba fDEB 562B4A54127DCC6eC3FB eA:bd:eA4FCDA5 5EcB 71,           sha1=0F 90a3ebAFfEDc d6 7AdBb7:cC a3 EDE9CE:89 AcEeec:F0 66:02 7EBb50 EE 7B:c75098 B0f5Dc2e 6A:C7:4DBE:F9 47:BC7d d7cA 58 B3:17f7f0:5Ed7 Ba:6bBc 2F 5C:7f:7B:65:dBC8 b9:fB:A757FE98aD EE fE:c00D 822444E8dd154804:15cD:D8eb37 5A 0BeC,                                                                      Ad:1EaB 504DF5 9D6D B1be 3B38:3d:3e:c944 53:d5,                           sha512=47 9acE 97F7:E22c28:c20B:0C081DCfEE C0de CCACa6 C8E5bd:Cc 1A:eE:40:5E 3f64:D0e4 68df:7D:bb:1B:8b1f 83:E2:47:B2:9Fbee8fED41c:c620:94AFDADdC9:e1:BA:3d5F:D9,                                                                     81ab:cFc0 fa0dd1 0d:F6:b62AE6bef98a:d1dc5d:fcAD3d e0 6102:5EdFbB345e158Ee0D4 aA8E:e2 bD57B5:0F 0Cfb:ed AE9C f0 E7 47 b19ACE:7Bfa:50E633 fB,                                                                28:D95e:95:F3fd72:Aa:C62017:64Ae:Bc 0F:3297:fc:c9 6Dea1F AB9De2b0:6D556fe3:9B1F e6cA:f0 B5 96 b4:d9:fAAe B900 6B:14 BAFBe9Ce Ed13 fc4E 3F:d617 49 9b Ea,                                                                             sha1=26C517 ca:ac32:a497 B2 cc ef 9D 1ADF 8E:64:EB9d621d:C9a3 AaC6 27a1 67Bd F6:012A af fabF:0BAB:C7FAEf0DaBEb 29 9f:3c:2ddd:BBce:4CD5:Fc F5bc 8276ee E7Ba5d4d0e:8fC2F92B 2E 65 2CE7Ba98 91b3A4 f6",
        trusted_certificates=[
            PublicKeyOrCert(
                name="name_example",
                data="data_example",
            )
        ],
        ws1_intelligence_credentials=WS1IntelligenceCredentials(
            data=WS1IntelligenceData(
                oauth_client=WS1IntelligenceOAuthClient(
                    client_id="client_id_example",
                    client_secret="client_secret_example",
                    scopes=[
                        "scopes_example"
                    ],
                    access_token_validity_secs=1,
                    refresh_token_validity_secs=1,
                    integration="integration_example",
                    source_system_id="source_system_id_example",
                    org_id="org_id_example",
,
,
                ),
                events_base_url="events_base_url_example",
                token_endpoint="token_endpoint_example",
                api_base_url="api_base_url_example",
            ),
        ),
    )
    try:
        # Update Workspace ONE Intelligence settings
        api_response = api_instance.update_ws1_intelligence_settings(
            body=body,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling WorkspaceOneIntelligenceSettingsApi->update_ws1_intelligence_settings: %s\n" % e)
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
[**WorkspaceOneIntelligenceSettings**](../../models/WorkspaceOneIntelligenceSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#update_ws1_intelligence_settings.ApiResponseForDefault) | successful operation

#### update_ws1_intelligence_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)
