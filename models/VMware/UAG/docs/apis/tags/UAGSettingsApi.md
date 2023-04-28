<a name="__pageTop"></a>
# openapi_client.apis.tags.uag_settings_api.UAGSettingsApi

All URIs are relative to */rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_or_update_settings**](#create_or_update_settings) | **put** /v1/config/settings | Create or update settings
[**get_settings**](#get_settings) | **get** /v1/config/settings | Get settings

# **create_or_update_settings**
<a name="create_or_update_settings"></a>
> Settings create_or_update_settings()

Create or update settings

Create settings if they do not exist; else, update the existing ones.

### Example

```python
import openapi_client
from openapi_client.apis.tags import uag_settings_api
from openapi_client.model.settings import Settings
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = uag_settings_api.UAGSettingsApi(api_client)

    # example passing only optional values
    body = Settings(
        general_settings=GeneralSettings(
            name="name_example",
            source="source_example",
            target="target_example",
            ds="ds_example",
            disk_mode="disk_mode_example",
            net_internet="net_internet_example",
            net_management_network="net_management_network_example",
            net_backend_network="net_backend_network_example",
            ip_mode0="ip_mode0_example",
            ip_mode1="ip_mode1_example",
            ip_mode2="ip_mode2_example",
            ip0="ip0_example",
            eth0_error_msg="eth0_error_msg_example",
            eth0_custom_config="DHCP^UseDNS=false;DHCP^UseNTP=false;",
            routes0="routes0_example",
            netmask0="netmask0_example",
            gateway0="gateway0_example",
            force_netmask0="force_netmask0_example",
            force_ipv6_prefix0="force_ipv6_prefix0_example",
            ip0_allocation_mode="STATICV4",
            default_gateway="default_gateway_example",
            v6_default_gateway="v6_default_gateway_example",
            ip1="ip1_example",
            eth1_error_msg="eth1_error_msg_example",
            eth1_custom_config="DHCP^UseDNS=false;DHCP^UseNTP=false;",
            routes1="routes1_example",
            netmask1="netmask1_example",
            gateway1="gateway1_example",
            force_netmask1="force_netmask1_example",
            force_ipv6_prefix1="force_ipv6_prefix1_example",
            ip1_allocation_mode="STATICV4",
            ip2="ip2_example",
            eth2_error_msg="eth2_error_msg_example",
            eth2_custom_config="DHCP^UseDNS=false;DHCP^UseNTP=false;",
            routes2="routes2_example",
            netmask2="netmask2_example",
            gateway2="gateway2_example",
            force_netmask2="force_netmask2_example",
            force_ipv6_prefix2="force_ipv6_prefix2_example",
            ip2_allocation_mode="STATICV4",
            deployment_option="deployment_option_example",
            dns="dns_example",
            dns0="dns0_example",
            forwardrules="forwardrules_example",
            v6ip0="v6ip0_example",
            v6ip1="v6ip1_example",
            v6ip2="v6ip2_example",
            ipv6prefix0="ipv6prefix0_example",
            ipv6prefix1="ipv6prefix1_example",
            ipv6prefix2="ipv6prefix2_example",
        ),
        system_settings=SystemSettings(
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
        ),
        edge_service_settings_list=EdgeServiceSettingsList(
            edge_service_settings_list=[
                EdgeServiceSettings()
            ],
        ),
        auth_method_settings_list=AuthMethodSettingsList(
            auth_method_settings_list=[
                AuthMethodSettings(
                    name="name_example",
                    class_name="class_name_example",
                    display_name="display_name_example",
                    jar_file="jar_file_example",
                    auth_method="auth_method_example",
                    version_num="version_num_example",
                )
            ],
        ),
        kerberos_key_tab_settings_list=KerberosKeyTabSettingsList(
            kerberos_key_tab_settings=[
                KerberosKeyTabSettings(
                    principal_name="principal_name_example",
                    key_tab="key_tab_example",
                    key_tab_file_path="key_tab_file_path_example",
                    realm="realm_example",
                )
            ],
        ),
        kerberos_realm_settings_list=KerberosRealmSettingsList(
            kerberos_realm_settings_list=[
                KerberosRealmSettings(
                    name="uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr",
                    kdc_host_name_list=[
                        "kdc_host_name_list_example"
                    ],
                    kdc_timeout=1,
                    no_of_wrps_using_this_realm=1,
                )
            ],
        ),
        certificate_wrapper=CertificateChainAndKeyWrapper(
            private_key_pem="private_key_pem_example",
            cert_chain_pem="cert_chain_pem_example",
        ),
,
        service_provider_metadata_list=SpMediaTypes(
            items=[
                SpMediaType(
                    sp_name="sp_name_example",
                    metadata_xml="metadata_xml_example",
                    assertion_lifetime=1,
                    links=dict(
                        "key": Link(
                            href="href_example",
                            params=dict(),
                        ),
                    ),
                )
            ],
            links=dict(),
        ),
        identity_provider_meta_data=CertificateChainAndKeyWrapper(),
        pfx_cert_store_wrapper=PfxCertStoreWrapper(
            pfx_keystore="pfx_keystore_example",
            password="password_example",
            alias="alias_example",
        ),
,
        idp_media_type=IdpMediaType(
            metadata_xml="metadata_xml_example",
            links=dict(),
        ),
        custom_branding_settings=CustomBrandingSettings(
            custom_branding_list=[
                CustomBranding(
                    resource_content="resource_content_example",
                    resource_name="resource_name_example",
                    resource_map_key="resource_map_key_example",
                )
            ],
        ),
        id_p_external_metadata_settings_list=IdPExternalMetadataSettingsList(
            id_p_external_metadata_settings_list=[
                IdPExternalMetadataSettings(
                    entity_id="entity_id_example",
                    metadata="metadata_example",
                    force_auth_n=True,
                    allow_unencrypted=True,
                    encryption_certificate_type="encryption_certificate_type_example",
                    certificate_chain_and_key_wrapper=CertificateChainAndKeyWrapper(),
                )
            ],
        ),
        device_policy_settings_list=DevicePolicySettingsList(
            device_policy_settings_list=[
                DevicePolicySettings()
            ],
        ),
        load_balancer_settings=LoadBalancerSettings(
            virtual_ip_address="virtual_ip_address_example",
            group_id=1,
            load_balancer_mode="DISABLED",
        ),
        jwt_settings_list=JWTSettingsList(
            jwt_settings_list=[
                JWTSettings(
                    name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
                    issuer="issuer_example",
                    jwt_type="CONSUMER",
                    json_web_key_set="json_web_key_set_example",
                    public_keys=[
                        PublicKeyOrCert()
                    ],
                    public_key_url_settings=ServerSettings(
                        url="url_example",
                        url_thumbprints="B00829:cc FFCfEe50C3Dc:c8 3DD7 F7678895 ce 1Cb7CB 8Dac EA:2B7fD63d:FF95 Be894E,                                                          sha384=E1 0D:c8:CFD5 bF486347F0D5 9aC71BE262:B58A fc D5:DA:7b:9A:60 f27f D7:c739b02297a194:C6:1509 99 28 60e5Cc:eDe3Cf1713 2cdD 6A8d3C:cd EA d3 2c 3b:9F 4A42:A0:931b31,                                                                    sha1=9f 1cB2,                                        AE 07bECA:62fAbCDF00:7470d9:8a4F 5fdCC8:A7 a59c8Af7 aC1C:E4e75538:D5:57Bdb3:AfCD:aeBA:76:9e ed0f AC:95:1535 d7 c6 2A37 47aE1748:E5:3f:bAA4Db DB81:31:f3:0aaDcC:aB:98c925AC 9cEc:D9 cA26Da BEcDEe:73ED61AC:6a 24:d3:7d4AF6dD Ad F6F3 bD 5D,                        md5=ba8e:28E5a2a2:EFBc9FeD e6bafc5e18:b6:12:39C6 72 dc1C59:bb 0a0Acc Cb2a:98 C3 ebe89ECE C8ac6d10 01dd e967:feBa 57 5a:0ceA:54 Bf 3D9A F43E:cEFB42:AC:4B 47aE52FBbD,                                                       sha384=71F0:De:AfE5:Dd b0Ce 3F:DE7f aa:76 9eBf:Ae:9C94:Bee2b2Efd9:39A4:B5:47d6 2CEE8D:CDDF BA:bfF1:7a:C8:74 4C,                                                                           sha1=7d:b924:ab0E:c7:b3 daa8:a6 1F:c589 76:D27aFE:bB2f ba79 994B88 DD:BE:e86ad9 0e:A5aC3bcc e8:7d:4eDa:Aa8dDbB354 EdCF 2008:49:48 8E6F:8FCb7B 5e7076Df:20bcceAf 55B1CA DFBFb3 bdbA 7B cE2DD09FEd bc:43:c7:d48113,                                         dE deEF:4f:1c:92AFE4 26 d4dF:30C034AF6b:F72CB12c:9B:a0:Ef:2E C2 BC4D 1a 3DF05416a4a5 DD:28,                                                            sha256=Bdf1 7f89:F2 b5F4 4d:CaF726Fe:cebaaDEE:e3:315Af5f7:eD3d d9:ee eEBB3dd8,                                                          8E:fa3f fde132c2:9185:98:da 5B:a6 55 e2:f823 A4 33D8fb56d53fe5:c4CB:8a ddfc 7f:Fdb875:DCC16362:3ECB:7884:66 EbA7a9 Db:e5:3a:3a C3 ffeFaA4C:Fea7:EB:c5:f3315F,                                                                        sha256=bd:94A822:3C:C805D9:DB f4A553 F6D9 ADD1Ab:FDFa:68B8 BA eBadFE fE69E94108 44:bA:ea 878dd2 Fc,                                c681b2eFc0,                                                                          eB2B 79 6d A430:7E:7Fec8D21:BA5C 6B973c734AE8:F35B Bd:f9F5:2Aa5 eA:dc0a 3a15d177652A50:dF:6c 5A:eC:E9D2D3:B8 16:8E 0Bd3 65,                                                                  9c 66:AD b8 dc Ad:e1Fcbe01dA0B F9:D1:af EFb3105E 78:37 4fc7 7F:7A 5202a6ccaE0eEB57:aeb576B2:9Fa597 d0 C605cc 48:fd9b7D cE783E41 bd:65:3409,                       b5 cB84:2a:AFFD eD5f2f:c7 25e7:15 cc be 6e 4c17:19Ae deA0B0:9b32 4Ab0 cf:C5:2969:BE:0AaF:A81E:66 A4 00:3B 393a918F67bD:037E:dC:0e fe:49e1D919:4A fD05 EA89b48cF7 AB16:7Beda59a CD 7b68 8Cb7,                 F8fd B06bCd6E e7 39:28 3A 9B2e9f7D40Ce08 8c8b:0ca5 21 aC,                                                 3E 3ea5 c72a C6 57:31fF4E4FFA:A3fCcc 1F2f6BA3 CDdfeB:9d fFfD:e2 7ace:1DDbABfd:bBD7 c87e 001abE5A48 4213 bA55dc:c1,                                                                                           A8FAD683 bcb3:f5:eBAae7ed2B eC2eA9:e3d660C0:29 Cd:Fda72E:B8:AF 8d:CC26:8532 26FE:29 Ca 7949cFbC 09cd fD:B5:D9 017e:9C0d fEbC09 81 fF5637:c563595D9D7E:e0D7:EC aFB9 Ab34:0c4d:cA5a:CeE7 C0BcB4 Efa7 D1:cB61,                                                   af:c5 cA:d2:0d7c6E:0233dF e4 aC BE:Da 62:e4:Cc 6327 caD7 4eC4 45 Ea 6d CA 3C:ad44BCbf f01e3E 1C 8e37 12A0 Ef2E:3d:a526 eD,                  B1:DC bC D3:dFAf:93 37:eD:6eF59C 32 F8bf:9Aa77b 15:82 fD 79 3C5F:83 aa B8 b48BD9 939A:30 4f D4:5E6c:54ae:a3 84FB4e91 aB 02:D4686eeB 3e:F3129C 1756Bd12 ce:ffDeFA Fa Ef D3 9b de 2E0E5D:7a Bf FDB6 547E 2CA3:dF 27eaBE7E:01:7A a8:54,                                             sha384=24afd2:8f:a37A92a52dE3344C:cC:E6 Fe:de:f4 8C:6C Cc:F6:5F8b,        Fc:35C2 17 CF:1b f1 f7fad5 1432Cc:b5c8:ab075475 0d d0bf:fb EdB8:3bCA40:34:B2:10dd:b67fdffEeb:5e 17:47 ED29:67 FBd8E0CA:1B:bD db eCF74C00 5742F35Ddff9 1F:C7,                                                         0eDae2a48fc4Db3d6e:bC6F4B 0C 48:9A 0dAbC5da dC:CA0834:F03a:Fc7a:38511D 2Cd4BeCd 599cfE:DafaB8 E1c5:8Add bB14 D1:2Da8:94d6a7F9:6Cd7 fDA3 d89b61:11 b1:cc:9c:F6 8a 4e b1 2943 Efba fDEB 562B4A54127DCC6eC3FB eA:bd:eA4FCDA5 5EcB 71,           sha1=0F 90a3ebAFfEDc d6 7AdBb7:cC a3 EDE9CE:89 AcEeec:F0 66:02 7EBb50 EE 7B:c75098 B0f5Dc2e 6A:C7:4DBE:F9 47:BC7d d7cA 58 B3:17f7f0:5Ed7 Ba:6bBc 2F 5C:7f:7B:65:dBC8 b9:fB:A757FE98aD EE fE:c00D 822444E8dd154804:15cD:D8eb37 5A 0BeC,                                                                      Ad:1EaB 504DF5 9D6D B1be 3B38:3d:3e:c944 53:d5,                           sha512=47 9acE 97F7:E22c28:c20B:0C081DCfEE C0de CCACa6 C8E5bd:Cc 1A:eE:40:5E 3f64:D0e4 68df:7D:bb:1B:8b1f 83:E2:47:B2:9Fbee8fED41c:c620:94AFDADdC9:e1:BA:3d5F:D9,                                                                     81ab:cFc0 fa0dd1 0d:F6:b62AE6bef98a:d1dc5d:fcAD3d e0 6102:5EdFbB345e158Ee0D4 aA8E:e2 bD57B5:0F 0Cfb:ed AE9C f0 E7 47 b19ACE:7Bfa:50E633 fB,                                                                28:D95e:95:F3fd72:Aa:C62017:64Ae:Bc 0F:3297:fc:c9 6Dea1F AB9De2b0:6D556fe3:9B1F e6cA:f0 B5 96 b4:d9:fAAe B900 6B:14 BAFBe9Ce Ed13 fc4E 3F:d617 49 9b Ea,                                                                             sha1=26C517 ca:ac32:a497 B2 cc ef 9D 1ADF 8E:64:EB9d621d:C9a3 AaC6 27a1 67Bd F6:012A af fabF:0BAB:C7FAEf0DaBEb 29 9f:3c:2ddd:BBce:4CD5:Fc F5bc 8276ee E7Ba5d4d0e:8fC2F92B 2E 65 2CE7Ba98 91b3A4 f6",
,
                        url_response_refresh_interval=1,
                    ),
                )
            ],
        ),
        jwt_issuer_settings_list=JWTIssuerSettingsList(
            jwt_issuer_settings_list=[
                JWTIssuerSettings(
                    name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
                    issuer="issuer_example",
                    jwt_type="CONSUMER",
                    json_web_key_set="json_web_key_set_example",
                    jwt_signing_pem_cert_settings=CertificateChainAndKeyWrapper(),
                    jwt_signing_pfx_cert_settings=PfxCertStoreWrapper(),
                    encryption_public_key=[
                        PublicKeyOrCert()
                    ],
                    encryption_public_key_url_settings=ServerSettings(),
                )
            ],
        ),
        workspace_one_intelligence_settings_list=WS1IntelligenceSettingsList(
            workspace_one_intelligence_settings_list=[
                WorkspaceOneIntelligenceSettings(
                    name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
                    encoded_credentials_file_content="encoded_credentials_file_content_example",
                    url_thumbprints="B00829:cc FFCfEe50C3Dc:c8 3DD7 F7678895 ce 1Cb7CB 8Dac EA:2B7fD63d:FF95 Be894E,                                                          sha384=E1 0D:c8:CFD5 bF486347F0D5 9aC71BE262:B58A fc D5:DA:7b:9A:60 f27f D7:c739b02297a194:C6:1509 99 28 60e5Cc:eDe3Cf1713 2cdD 6A8d3C:cd EA d3 2c 3b:9F 4A42:A0:931b31,                                                                    sha1=9f 1cB2,                                        AE 07bECA:62fAbCDF00:7470d9:8a4F 5fdCC8:A7 a59c8Af7 aC1C:E4e75538:D5:57Bdb3:AfCD:aeBA:76:9e ed0f AC:95:1535 d7 c6 2A37 47aE1748:E5:3f:bAA4Db DB81:31:f3:0aaDcC:aB:98c925AC 9cEc:D9 cA26Da BEcDEe:73ED61AC:6a 24:d3:7d4AF6dD Ad F6F3 bD 5D,                        md5=ba8e:28E5a2a2:EFBc9FeD e6bafc5e18:b6:12:39C6 72 dc1C59:bb 0a0Acc Cb2a:98 C3 ebe89ECE C8ac6d10 01dd e967:feBa 57 5a:0ceA:54 Bf 3D9A F43E:cEFB42:AC:4B 47aE52FBbD,                                                       sha384=71F0:De:AfE5:Dd b0Ce 3F:DE7f aa:76 9eBf:Ae:9C94:Bee2b2Efd9:39A4:B5:47d6 2CEE8D:CDDF BA:bfF1:7a:C8:74 4C,                                                                           sha1=7d:b924:ab0E:c7:b3 daa8:a6 1F:c589 76:D27aFE:bB2f ba79 994B88 DD:BE:e86ad9 0e:A5aC3bcc e8:7d:4eDa:Aa8dDbB354 EdCF 2008:49:48 8E6F:8FCb7B 5e7076Df:20bcceAf 55B1CA DFBFb3 bdbA 7B cE2DD09FEd bc:43:c7:d48113,                                         dE deEF:4f:1c:92AFE4 26 d4dF:30C034AF6b:F72CB12c:9B:a0:Ef:2E C2 BC4D 1a 3DF05416a4a5 DD:28,                                                            sha256=Bdf1 7f89:F2 b5F4 4d:CaF726Fe:cebaaDEE:e3:315Af5f7:eD3d d9:ee eEBB3dd8,                                                          8E:fa3f fde132c2:9185:98:da 5B:a6 55 e2:f823 A4 33D8fb56d53fe5:c4CB:8a ddfc 7f:Fdb875:DCC16362:3ECB:7884:66 EbA7a9 Db:e5:3a:3a C3 ffeFaA4C:Fea7:EB:c5:f3315F,                                                                        sha256=bd:94A822:3C:C805D9:DB f4A553 F6D9 ADD1Ab:FDFa:68B8 BA eBadFE fE69E94108 44:bA:ea 878dd2 Fc,                                c681b2eFc0,                                                                          eB2B 79 6d A430:7E:7Fec8D21:BA5C 6B973c734AE8:F35B Bd:f9F5:2Aa5 eA:dc0a 3a15d177652A50:dF:6c 5A:eC:E9D2D3:B8 16:8E 0Bd3 65,                                                                  9c 66:AD b8 dc Ad:e1Fcbe01dA0B F9:D1:af EFb3105E 78:37 4fc7 7F:7A 5202a6ccaE0eEB57:aeb576B2:9Fa597 d0 C605cc 48:fd9b7D cE783E41 bd:65:3409,                       b5 cB84:2a:AFFD eD5f2f:c7 25e7:15 cc be 6e 4c17:19Ae deA0B0:9b32 4Ab0 cf:C5:2969:BE:0AaF:A81E:66 A4 00:3B 393a918F67bD:037E:dC:0e fe:49e1D919:4A fD05 EA89b48cF7 AB16:7Beda59a CD 7b68 8Cb7,                 F8fd B06bCd6E e7 39:28 3A 9B2e9f7D40Ce08 8c8b:0ca5 21 aC,                                                 3E 3ea5 c72a C6 57:31fF4E4FFA:A3fCcc 1F2f6BA3 CDdfeB:9d fFfD:e2 7ace:1DDbABfd:bBD7 c87e 001abE5A48 4213 bA55dc:c1,                                                                                           A8FAD683 bcb3:f5:eBAae7ed2B eC2eA9:e3d660C0:29 Cd:Fda72E:B8:AF 8d:CC26:8532 26FE:29 Ca 7949cFbC 09cd fD:B5:D9 017e:9C0d fEbC09 81 fF5637:c563595D9D7E:e0D7:EC aFB9 Ab34:0c4d:cA5a:CeE7 C0BcB4 Efa7 D1:cB61,                                                   af:c5 cA:d2:0d7c6E:0233dF e4 aC BE:Da 62:e4:Cc 6327 caD7 4eC4 45 Ea 6d CA 3C:ad44BCbf f01e3E 1C 8e37 12A0 Ef2E:3d:a526 eD,                  B1:DC bC D3:dFAf:93 37:eD:6eF59C 32 F8bf:9Aa77b 15:82 fD 79 3C5F:83 aa B8 b48BD9 939A:30 4f D4:5E6c:54ae:a3 84FB4e91 aB 02:D4686eeB 3e:F3129C 1756Bd12 ce:ffDeFA Fa Ef D3 9b de 2E0E5D:7a Bf FDB6 547E 2CA3:dF 27eaBE7E:01:7A a8:54,                                             sha384=24afd2:8f:a37A92a52dE3344C:cC:E6 Fe:de:f4 8C:6C Cc:F6:5F8b,        Fc:35C2 17 CF:1b f1 f7fad5 1432Cc:b5c8:ab075475 0d d0bf:fb EdB8:3bCA40:34:B2:10dd:b67fdffEeb:5e 17:47 ED29:67 FBd8E0CA:1B:bD db eCF74C00 5742F35Ddff9 1F:C7,                                                         0eDae2a48fc4Db3d6e:bC6F4B 0C 48:9A 0dAbC5da dC:CA0834:F03a:Fc7a:38511D 2Cd4BeCd 599cfE:DafaB8 E1c5:8Add bB14 D1:2Da8:94d6a7F9:6Cd7 fDA3 d89b61:11 b1:cc:9c:F6 8a 4e b1 2943 Efba fDEB 562B4A54127DCC6eC3FB eA:bd:eA4FCDA5 5EcB 71,           sha1=0F 90a3ebAFfEDc d6 7AdBb7:cC a3 EDE9CE:89 AcEeec:F0 66:02 7EBb50 EE 7B:c75098 B0f5Dc2e 6A:C7:4DBE:F9 47:BC7d d7cA 58 B3:17f7f0:5Ed7 Ba:6bBc 2F 5C:7f:7B:65:dBC8 b9:fB:A757FE98aD EE fE:c00D 822444E8dd154804:15cD:D8eb37 5A 0BeC,                                                                      Ad:1EaB 504DF5 9D6D B1be 3B38:3d:3e:c944 53:d5,                           sha512=47 9acE 97F7:E22c28:c20B:0C081DCfEE C0de CCACa6 C8E5bd:Cc 1A:eE:40:5E 3f64:D0e4 68df:7D:bb:1B:8b1f 83:E2:47:B2:9Fbee8fED41c:c620:94AFDADdC9:e1:BA:3d5F:D9,                                                                     81ab:cFc0 fa0dd1 0d:F6:b62AE6bef98a:d1dc5d:fcAD3d e0 6102:5EdFbB345e158Ee0D4 aA8E:e2 bD57B5:0F 0Cfb:ed AE9C f0 E7 47 b19ACE:7Bfa:50E633 fB,                                                                28:D95e:95:F3fd72:Aa:C62017:64Ae:Bc 0F:3297:fc:c9 6Dea1F AB9De2b0:6D556fe3:9B1F e6cA:f0 B5 96 b4:d9:fAAe B900 6B:14 BAFBe9Ce Ed13 fc4E 3F:d617 49 9b Ea,                                                                             sha1=26C517 ca:ac32:a497 B2 cc ef 9D 1ADF 8E:64:EB9d621d:C9a3 AaC6 27a1 67Bd F6:012A af fabF:0BAB:C7FAEf0DaBEb 29 9f:3c:2ddd:BBce:4CD5:Fc F5bc 8276ee E7Ba5d4d0e:8fC2F92B 2E 65 2CE7Ba98 91b3A4 f6",
,
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
            ],
        ),
        workspace_one_intelligence_data_settings=WorkspaceOneIntelligenceDataSettings(
            enabled=True,
            name="name_example",
            update_interval=1,
        ),
        outbound_proxy_settings_list=OutboundProxySettingsList(
            outbound_proxy_settings_list=[
                OutboundProxySettings(
                    name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
                    proxy_type="HTTP",
                    proxy_url="proxy_url_example",
                    included_hosts=[
                        "included_hosts_example"
                    ],
,
                )
            ],
        ),
        ocsp_signing_cert_list=OCSPSigningCertList(
,
        ),
        package_updates_settings=PackageUpdateSettings(
            package_updates_scheme="OFF",
            package_updates_osurl="package_updates_osurl_example",
            package_updates_url="package_updates_url_example",
,
        ),
        admin_users_list=AdminUsersList(
            admin_users_list=[
                AdminUser(
                    name="name_example",
                    password="password_example",
                    user_id="user_id_example",
                    enabled=True,
                    roles=[
                        "ROLE_ADMIN"
                    ],
                    admin_password_set_time="admin_password_set_time_example",
                    no_of_days_remaining_for_pwd_expiry=1,
                    user_type="INTERNAL",
                    admin_monitoring_password_pre_expired=True,
                )
            ],
        ),
        custom_executable_list=CustomExecutableList(
            custom_executable_list=[
                ResourceSettings(
                    resource_url_settings=ServerSettings(),
                    hosted_resource_metadata=HostedResourceMetadata(
                        name="N p}{ML_M-MMpN{-{p}L-.M{-{_M.-MN{{NM{}-}M]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",
                        path="path_example",
                        sha256_sum="sha256_sum_example",
                        params="params_example",
                        flags=Flags(
,
                        ),
                        executable="executable_example",
                        is_obtainedfrom_url=True,
                        _file_type="Windows",
,
                        os_type="os_type_example",
                    ),
                )
            ],
        ),
        syslog_settings=SyslogSettings(
            syslog_server_settings=[
                SyslogServerSettings(
                    syslog_category="syslog_category_example",
                    syslog_category_list=[
                        "ALL"
                    ],
                    syslog_format="TEXT",
                    sys_log_type="UDP",
                    syslog_system_messages_enabled_v2=True,
                    syslog_url="syslog_url_example",
                    mqtt_topic="mqtt_topic_example",
                    syslog_setting_name="zBAMDTMv",
                    tls_syslog_server_settings=TlsSyslogServerSettings(),
                    tls_mqtt_server_settings=TlsMqttServerSettings(
                        mqtt_client_cert_cert_pem="mqtt_client_cert_cert_pem_example",
                        mqtt_client_cert_key_pem="mqtt_client_cert_key_pem_example",
                        mqtt_server_ca_cert_pem="mqtt_server_ca_cert_pem_example",
                    ),
                )
            ],
        ),
        admin_saml_settings=AdminSAMLSettings(
            enable=True,
            entity_id="entity_id_example",
        ),
        security_agent_settings_list=SecurityAgentSettingsList(
            security_agent_settings_list=[
                SecurityAgentSettings()
            ],
        ),
    )
    try:
        # Create or update settings
        api_response = api_instance.create_or_update_settings(
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling UAGSettingsApi->create_or_update_settings: %s\n" % e)
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
[**Settings**](../../models/Settings.md) |  | 


### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | [ApiResponseFor200](#create_or_update_settings.ApiResponseFor200) | successful operation

#### create_or_update_settings.ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

# SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**Settings**](../../models/Settings.md) |  | 


### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

# **get_settings**
<a name="get_settings"></a>
> get_settings()

Get settings

Get the settings which contain configuration info for UAG

### Example

```python
import openapi_client
from openapi_client.apis.tags import uag_settings_api
from pprint import pprint
# Defining the host is optional and defaults to /rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "/rest"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = uag_settings_api.UAGSettingsApi(api_client)

    # example passing only optional values
    query_params = {
        'format': "JSON",
    }
    try:
        # Get settings
        api_response = api_instance.get_settings(
            query_params=query_params,
        )
    except openapi_client.ApiException as e:
        print("Exception when calling UAGSettingsApi->get_settings: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
query_params | RequestQueryParams | |
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### query_params
#### RequestQueryParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
format | FormatSchema | | optional


# FormatSchema

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
str,  | str,  |  | must be one of ["JSON", "INI", ] if omitted the server will use the default value of "JSON"

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
default | [ApiResponseForDefault](#get_settings.ApiResponseForDefault) | successful operation

#### get_settings.ApiResponseForDefault
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[] |  |
headers | Unset | headers were not defined |

### Authorization

No authorization required

[[Back to top]](#__pageTop) [[Back to API list]](../../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../../README.md#documentation-for-models) [[Back to README]](../../../README.md)

