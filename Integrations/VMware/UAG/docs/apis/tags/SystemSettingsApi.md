<a name="__pageTop"></a>
# openapi_client.apis.tags.system_settings_api.SystemSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_or_update_system_settings**](#create_or_update_system_settings) | **put** /v1/config/system | Create or update system settings
[**get_system_settings**](#get_system_settings) | **get** /v1/config/system | Get system settings

# **create_or_update_system_settings**
<a name="create_or_update_system_settings"></a>
> SystemSettings create_or_update_system_settings()

Create or update system settings

Create a system settings if it doesn't exist; else, update the existing one.

### Example

```python
import openapi_client
from openapi_client.apis.tags import system_settings_api
from openapi_client.model.system_settings import SystemSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = system_settings_api.SystemSettingsApi(api_client)

    # example passing only optional values
    body = SystemSettings(
        fips_enabled=True,
        admin_password_expiration_days=1,
        admin_session_idle_timeout_minutes=1,
        admin_max_concurrent_sessions=1,
        root_password_expiration_days=1,
        root_session_idle_timeout_seconds=1,
        os_login_username="os_login_username_example",
        os_max_login_limit="os_max_login_limit_example",
        monitoring_users_password_expiration_days=0,
        admin_password_policy_settings=PasswordPolicySettings(
            password_policy_min_len=1,
            password_policy_min_class=1,
            password_policy_difok=1,
            password_policy_unlock_time=1,
            password_policy_failed_lockout=1,
        ),
,
        cipher_suites="cipher_suites_example",
        outbound_cipher_suites="outbound_cipher_suites_example",
        ssl_provider="JDK",
        tls_named_groups="tls_named_groups_example",
        tls_signature_schemes="tls_signature_schemes_example",
        ssl30_enabled=True,
        tls10_enabled=True,
        tls11_enabled=True,
        tls12_enabled=True,
        tls13_enabled=True,
        admin_disclaimer_text="admin_disclaimer_text_example",
        syslog_url="syslog_url_example",
        syslog_audit_url="syslog_audit_url_example",
        sys_log_type="UDP",
        syslog_server_ca_cert_pem="syslog_server_ca_cert_pem_example",
        syslog_client_cert_cert_pem="syslog_client_cert_cert_pem_example",
        syslog_client_cert_key_pem="syslog_client_cert_key_pem_example",
        tls_syslog_server_settings=[
            TlsSyslogServerSettings(
                hostname="hostname_example",
                port=1,
                accepted_peer="accepted_peer_example",
                syslog_server_ca_cert_pem_v2="syslog_server_ca_cert_pem_v2_example",
                syslog_client_cert_pem_v2="syslog_client_cert_pem_v2_example",
                syslog_client_cert_key_pem_v2="syslog_client_cert_key_pem_v2_example",
            )
        ],
        health_check_url="health_check_url_example",
        enable_http_health_monitor=True,
        cookies_to_be_cached="cookies_to_be_cached_example",
        ip_mode="STATICV4",
        ip_modefor_nic2="STATICV4",
        ip_modefor_nic3="STATICV4",
        default_redirect_host="default_redirect_host_example",
        session_timeout=0,
        request_timeout_msec=1,
        body_receive_timeout_msec=1,
        authentication_timeout=0,
        quiesce_mode=True,
        monitor_interval=0,
        saml_cert_rollover_supported=True,
        http_connection_timeout=1,
        tls_port_sharing_enabled=True,
        uag_name="uag_name_example",
        ceip_enabled=True,
        admin_cert_rolled_back=True,
        client_connection_idle_timeout=1,
        ssh_enabled=True,
        ssh_password_access_enabled=True,
        ssh_key_access_enabled=True,
        ssh_interface="ssh_interface_example",
        ssh_port="ssh_port_example",
        ssh_login_banner_text="ssh_login_banner_text_example",
        ssh_public_keys=[
            SshPublicKey(
                name="name_example",
                data="data_example",
            )
        ],
        dns="dns_example",
        dns_search="dns_search_example",
        snmp_enabled=True,
        snmp_settings=SnmpSettings(
            version="V1_V2C",
            usm_user="usm_user_example",
            engine_id="engine_id_example",
            security_level="NO_AUTH_NO_PRIV",
            auth_password="auth_password_example",
            privacy_algorithm="AES",
            privacy_password="privacy_password_example",
            auth_algorithm="auth_algorithm_example",
        ),
        host_clock_sync_supported=True,
        host_clock_sync_enabled=True,
        ntp_servers="ntp_servers_example",
        fall_back_ntp_servers="fall_back_ntp_servers_example",
        clock_skew_tolerance=1,
        max_connections_allowed_per_session=1,
        max_system_cpu_allowed=1,
        allowed_host_header_values="allowed_host_header_values_example",
        enabled_advanced_features="enabled_advanced_features_example",
        secure_random_source="secure_random_source_example",
        forced_restart=True,
        core_dump_settings=CoreDumpSettings(
            max_size_mb=16,
            max_time_seconds=0,
        ),
        extended_server_cert_validation_enabled=True,
        commands_first_boot="commands_first_boot_example",
        commands_every_boot="commands_every_boot_example",
        ds_compliance_os=True,
        unrecognized_sessions_monitoring_enabled=True,
    )
    try:
        # Create or update system settings
        api_response = api_instance.create_or_update_system_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SystemSettingsApi->create_or_update_system_settings: %s\n" % e)
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
[**SystemSettings**](../../models/SystemSettings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_system_settings.ApiResponseFor200) | successful operation

#### create_or_update_system_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SystemSettings**](../../models/SystemSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_system_settings**
<a name="get_system_settings"></a>
> SystemSettings get_system_settings()

Get system settings

Get the settings which contain configuration info for the Unified Access Gateway

### Example

```python
import openapi_client
from openapi_client.apis.tags import system_settings_api
from openapi_client.model.system_settings import SystemSettings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = system_settings_api.SystemSettingsApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get system settings
        api_response = api_instance.get_system_settings()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling SystemSettingsApi->get_system_settings: %s\n" % e)
```
### Parameters
This endpoint does not need any parameter.

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#get_system_settings.ApiResponseFor200) | successful operation

#### get_system_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**SystemSettings**](../../models/SystemSettings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

