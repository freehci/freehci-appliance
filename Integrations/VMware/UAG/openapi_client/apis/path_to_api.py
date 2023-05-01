import typing_extensions

from openapi_client.paths import PathValues
from openapi_client.apis.paths.v1_config_authmethod_securid_auth import V1ConfigAuthmethodSecuridAuth
from openapi_client.apis.paths.v1_config_authmethod_certificate_auth import V1ConfigAuthmethodCertificateAuth
from openapi_client.apis.paths.v1_config_authmethod_radius_auth import V1ConfigAuthmethodRadiusAuth
from openapi_client.apis.paths.v1_config_adminusers import V1ConfigAdminusers
from openapi_client.apis.paths.v1_config_adminusers_change_password import V1ConfigAdminusersChangePassword
from openapi_client.apis.paths.v1_config_adminusers_log_admin_user_action_action import V1ConfigAdminusersLogAdminUserActionAction
from openapi_client.apis.paths.v1_config_adminusers_id import V1ConfigAdminusersId
from openapi_client.apis.paths.v1_config_adminusers_privileges_id import V1ConfigAdminusersPrivilegesId
from openapi_client.apis.paths.v1_config_adminusers_saml_auth import V1ConfigAdminusersSamlAuth
from openapi_client.apis.paths.v1_config_authmethod_name import V1ConfigAuthmethodName
from openapi_client.apis.paths.v1_config_authmethod_reset_name import V1ConfigAuthmethodResetName
from openapi_client.apis.paths.v1_config_authmethod_ocsp_file_names import V1ConfigAuthmethodOcspFileNames
from openapi_client.apis.paths.v1_config_authmethod import V1ConfigAuthmethod
from openapi_client.apis.paths.v1_config_authmethod_ocsp_certificate import V1ConfigAuthmethodOcspCertificate
from openapi_client.apis.paths.v1_config_authmethod_ocsp import V1ConfigAuthmethodOcsp
from openapi_client.apis.paths.v1_config_custom_branding_save_custom_branding import V1ConfigCustomBrandingSaveCustomBranding
from openapi_client.apis.paths.v1_config_custom_branding import V1ConfigCustomBranding
from openapi_client.apis.paths.v1_config_devicepolicy_name import V1ConfigDevicepolicyName
from openapi_client.apis.paths.v1_config_devicepolicy_opswat import V1ConfigDevicepolicyOpswat
from openapi_client.apis.paths.v1_config_devicepolicy_ws1_intelligence_risk_score import V1ConfigDevicepolicyWs1IntelligenceRiskScore
from openapi_client.apis.paths.v1_config_devicepolicy_available import V1ConfigDevicepolicyAvailable
from openapi_client.apis.paths.v1_config_devicepolicy_configured import V1ConfigDevicepolicyConfigured
from openapi_client.apis.paths.v1_config_devicepolicy import V1ConfigDevicepolicy
from openapi_client.apis.paths.v1_config_disclaimer import V1ConfigDisclaimer
from openapi_client.apis.paths.v1_config_edgeservice_view import V1ConfigEdgeserviceView
from openapi_client.apis.paths.v1_config_edgeservice import V1ConfigEdgeservice
from openapi_client.apis.paths.v1_config_edgeservice_edge_service_type import V1ConfigEdgeserviceEdgeServiceType
from openapi_client.apis.paths.v1_config_edgeservice_find_configured_edge_services_and_auth_methods import V1ConfigEdgeserviceFindConfiguredEdgeServicesAndAuthMethods
from openapi_client.apis.paths.v1_config_edgeservice_edge_service_type_instance_id import V1ConfigEdgeserviceEdgeServiceTypeInstanceId
from openapi_client.apis.paths.v1_config_edgeservice_available_horizon_auth_methods import V1ConfigEdgeserviceAvailableHorizonAuthMethods
from openapi_client.apis.paths.v1_config_edgeservice_webreverseproxy import V1ConfigEdgeserviceWebreverseproxy
from openapi_client.apis.paths.v1_config_edgeservice_tunnelgateway import V1ConfigEdgeserviceTunnelgateway
from openapi_client.apis.paths.v1_config_edgeservice_tunnelproxy import V1ConfigEdgeserviceTunnelproxy
from openapi_client.apis.paths.v1_config_edgeservice_seg import V1ConfigEdgeserviceSeg
from openapi_client.apis.paths.v1_config_edgeservice_contentgateway import V1ConfigEdgeserviceContentgateway
from openapi_client.apis.paths.v1_config_feature import V1ConfigFeature
from openapi_client.apis.paths.v1_config_resource_upload import V1ConfigResourceUpload
from openapi_client.apis.paths.v1_config_resource import V1ConfigResource
from openapi_client.apis.paths.v1_config_resource_name_file_type import V1ConfigResourceNameFileType
from openapi_client.apis.paths.v1_config_resource_delete_uploaded_resource_name_file_type import V1ConfigResourceDeleteUploadedResourceNameFileType
from openapi_client.apis.paths.v1_config_resource_upload_settings_settings_id_file_type import V1ConfigResourceUploadSettingsSettingsIdFileType
from openapi_client.apis.paths.v1_config_resource_delete_uploaded_resource_settings_settings_id_file_type import V1ConfigResourceDeleteUploadedResourceSettingsSettingsIdFileType
from openapi_client.apis.paths.v1_config_general import V1ConfigGeneral
from openapi_client.apis.paths.v1_config_idp_ext_metadata import V1ConfigIdpExtMetadata
from openapi_client.apis.paths.v1_config_idp_ext_metadata_entity_id__ import V1ConfigIdpExtMetadataEntityID
from openapi_client.apis.paths.v1_config_idp_metadata_host_name import V1ConfigIdpMetadataHostName
from openapi_client.apis.paths.v1_config_idp_metadata import V1ConfigIdpMetadata
from openapi_client.apis.paths.v1_config_jwt_issuer_name import V1ConfigJwtIssuerName
from openapi_client.apis.paths.v1_config_jwt_issuer import V1ConfigJwtIssuer
from openapi_client.apis.paths.v1_config_jwt_name import V1ConfigJwtName
from openapi_client.apis.paths.v1_config_jwt import V1ConfigJwt
from openapi_client.apis.paths.v1_config_kerberos_realm_realm_name import V1ConfigKerberosRealmRealmName
from openapi_client.apis.paths.v1_config_kerberos_keytab_principal_name import V1ConfigKerberosKeytabPrincipalName
from openapi_client.apis.paths.v1_config_kerberos_keytab import V1ConfigKerberosKeytab
from openapi_client.apis.paths.v1_config_kerberos_realm import V1ConfigKerberosRealm
from openapi_client.apis.paths.v1_config_loadbalancer_state import V1ConfigLoadbalancerState
from openapi_client.apis.paths.v1_config_loadbalancer_settings import V1ConfigLoadbalancerSettings
from openapi_client.apis.paths.v1_config_loadbalancer_stats import V1ConfigLoadbalancerStats
from openapi_client.apis.paths.v1_monitor_set_log_levels import V1MonitorSetLogLevels
from openapi_client.apis.paths.v1_monitor_stats import V1MonitorStats
from openapi_client.apis.paths.v1_monitor_set_utserver_log_level_log_level import V1MonitorSetUtserverLogLevelLogLevel
from openapi_client.apis.paths.v1_monitor_seg_health_stats import V1MonitorSegHealthStats
from openapi_client.apis.paths.v1_monitor_seg_diagnostics_identifier import V1MonitorSegDiagnosticsIdentifier
from openapi_client.apis.paths.v1_monitor_seg_cache_id import V1MonitorSegCacheId
from openapi_client.apis.paths.v1_monitor_support_archive import V1MonitorSupportArchive
from openapi_client.apis.paths.v1_monitor_get_log_levels import V1MonitorGetLogLevels
from openapi_client.apis.paths.v1_monitor_reset_log_levels import V1MonitorResetLogLevels
from openapi_client.apis.paths.v1_config_nic_nic import V1ConfigNicNic
from openapi_client.apis.paths.v1_config_nic import V1ConfigNic
from openapi_client.apis.paths.v1_config_proxy import V1ConfigProxy
from openapi_client.apis.paths.v1_config_proxy_name import V1ConfigProxyName
from openapi_client.apis.paths.v1_config_packageupdates import V1ConfigPackageupdates
from openapi_client.apis.paths.v1_config_security_agent_name import V1ConfigSecurityAgentName
from openapi_client.apis.paths.v1_config_security_agent_configured import V1ConfigSecurityAgentConfigured
from openapi_client.apis.paths.v1_config_security_agent_available import V1ConfigSecurityAgentAvailable
from openapi_client.apis.paths.v1_config_sp_ext_metadata_sp_external_host_name_instance_id import V1ConfigSpExtMetadataSpExternalHostNameInstanceId
from openapi_client.apis.paths.v1_config_sp_ext_metadata_sp_external_host_name import V1ConfigSpExtMetadataSpExternalHostName
from openapi_client.apis.paths.v1_config_sp_metadata_name import V1ConfigSpMetadataName
from openapi_client.apis.paths.v1_config_sp_metadata import V1ConfigSpMetadata
from openapi_client.apis.paths.v1_config_settings import V1ConfigSettings
from openapi_client.apis.paths.v1_config_certs_ssl_pfx_entity import V1ConfigCertsSslPfxEntity
from openapi_client.apis.paths.v1_config_certs_ssl_pfx import V1ConfigCertsSslPfx
from openapi_client.apis.paths.v1_config_certs_ssl import V1ConfigCertsSsl
from openapi_client.apis.paths.v1_config_certs_ssl_entity import V1ConfigCertsSslEntity
from openapi_client.apis.paths.v1_config_syslog import V1ConfigSyslog
from openapi_client.apis.paths.v1_config_syslog_host_name import V1ConfigSyslogHostName
from openapi_client.apis.paths.v1_config_system import V1ConfigSystem
from openapi_client.apis.paths.v1_config_ws1intelligencedata import V1ConfigWs1intelligencedata
from openapi_client.apis.paths.v1_config_ws1intelligence_name import V1ConfigWs1intelligenceName
from openapi_client.apis.paths.v1_config_ws1intelligence import V1ConfigWs1intelligence

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.V1_CONFIG_AUTHMETHOD_SECURIDAUTH: V1ConfigAuthmethodSecuridAuth,
        PathValues.V1_CONFIG_AUTHMETHOD_CERTIFICATEAUTH: V1ConfigAuthmethodCertificateAuth,
        PathValues.V1_CONFIG_AUTHMETHOD_RADIUSAUTH: V1ConfigAuthmethodRadiusAuth,
        PathValues.V1_CONFIG_ADMINUSERS: V1ConfigAdminusers,
        PathValues.V1_CONFIG_ADMINUSERS_CHANGEPASSWORD: V1ConfigAdminusersChangePassword,
        PathValues.V1_CONFIG_ADMINUSERS_LOG_ADMIN_USER_ACTION_ACTION: V1ConfigAdminusersLogAdminUserActionAction,
        PathValues.V1_CONFIG_ADMINUSERS_ID: V1ConfigAdminusersId,
        PathValues.V1_CONFIG_ADMINUSERS_PRIVILEGES_ID: V1ConfigAdminusersPrivilegesId,
        PathValues.V1_CONFIG_ADMINUSERS_SAML_AUTH: V1ConfigAdminusersSamlAuth,
        PathValues.V1_CONFIG_AUTHMETHOD_NAME: V1ConfigAuthmethodName,
        PathValues.V1_CONFIG_AUTHMETHOD_RESET_NAME: V1ConfigAuthmethodResetName,
        PathValues.V1_CONFIG_AUTHMETHOD_OCSP_FILE_NAMES: V1ConfigAuthmethodOcspFileNames,
        PathValues.V1_CONFIG_AUTHMETHOD: V1ConfigAuthmethod,
        PathValues.V1_CONFIG_AUTHMETHOD_OCSP_CERTIFICATE: V1ConfigAuthmethodOcspCertificate,
        PathValues.V1_CONFIG_AUTHMETHOD_OCSP: V1ConfigAuthmethodOcsp,
        PathValues.V1_CONFIG_CUSTOM_BRANDING_SAVE_CUSTOM_BRANDING: V1ConfigCustomBrandingSaveCustomBranding,
        PathValues.V1_CONFIG_CUSTOM_BRANDING: V1ConfigCustomBranding,
        PathValues.V1_CONFIG_DEVICEPOLICY_NAME: V1ConfigDevicepolicyName,
        PathValues.V1_CONFIG_DEVICEPOLICY_OPSWAT: V1ConfigDevicepolicyOpswat,
        PathValues.V1_CONFIG_DEVICEPOLICY_WS1INTELLIGENCE_RISK_SCORE: V1ConfigDevicepolicyWs1IntelligenceRiskScore,
        PathValues.V1_CONFIG_DEVICEPOLICY_AVAILABLE: V1ConfigDevicepolicyAvailable,
        PathValues.V1_CONFIG_DEVICEPOLICY_CONFIGURED: V1ConfigDevicepolicyConfigured,
        PathValues.V1_CONFIG_DEVICEPOLICY: V1ConfigDevicepolicy,
        PathValues.V1_CONFIG_DISCLAIMER: V1ConfigDisclaimer,
        PathValues.V1_CONFIG_EDGESERVICE_VIEW: V1ConfigEdgeserviceView,
        PathValues.V1_CONFIG_EDGESERVICE: V1ConfigEdgeservice,
        PathValues.V1_CONFIG_EDGESERVICE_EDGE_SERVICE_TYPE: V1ConfigEdgeserviceEdgeServiceType,
        PathValues.V1_CONFIG_EDGESERVICE_FIND_CONFIGURED_EDGE_SERVICES_AND_AUTH_METHODS: V1ConfigEdgeserviceFindConfiguredEdgeServicesAndAuthMethods,
        PathValues.V1_CONFIG_EDGESERVICE_EDGE_SERVICE_TYPE_INSTANCE_ID: V1ConfigEdgeserviceEdgeServiceTypeInstanceId,
        PathValues.V1_CONFIG_EDGESERVICE_AVAILABLE_HORIZON_AUTH_METHODS: V1ConfigEdgeserviceAvailableHorizonAuthMethods,
        PathValues.V1_CONFIG_EDGESERVICE_WEBREVERSEPROXY: V1ConfigEdgeserviceWebreverseproxy,
        PathValues.V1_CONFIG_EDGESERVICE_TUNNELGATEWAY: V1ConfigEdgeserviceTunnelgateway,
        PathValues.V1_CONFIG_EDGESERVICE_TUNNELPROXY: V1ConfigEdgeserviceTunnelproxy,
        PathValues.V1_CONFIG_EDGESERVICE_SEG: V1ConfigEdgeserviceSeg,
        PathValues.V1_CONFIG_EDGESERVICE_CONTENTGATEWAY: V1ConfigEdgeserviceContentgateway,
        PathValues.V1_CONFIG_FEATURE: V1ConfigFeature,
        PathValues.V1_CONFIG_RESOURCE_UPLOAD: V1ConfigResourceUpload,
        PathValues.V1_CONFIG_RESOURCE: V1ConfigResource,
        PathValues.V1_CONFIG_RESOURCE_NAME_FILE_TYPE: V1ConfigResourceNameFileType,
        PathValues.V1_CONFIG_RESOURCE_DELETE_UPLOADED_RESOURCE_NAME_FILE_TYPE: V1ConfigResourceDeleteUploadedResourceNameFileType,
        PathValues.V1_CONFIG_RESOURCE_UPLOAD_SETTINGS_SETTINGS_ID_FILE_TYPE: V1ConfigResourceUploadSettingsSettingsIdFileType,
        PathValues.V1_CONFIG_RESOURCE_DELETE_UPLOADED_RESOURCE_SETTINGS_SETTINGS_ID_FILE_TYPE: V1ConfigResourceDeleteUploadedResourceSettingsSettingsIdFileType,
        PathValues.V1_CONFIG_GENERAL: V1ConfigGeneral,
        PathValues.V1_CONFIG_IDPEXTMETADATA: V1ConfigIdpExtMetadata,
        PathValues.V1_CONFIG_IDPEXTMETADATA_ENTITY_ID_: V1ConfigIdpExtMetadataEntityID,
        PathValues.V1_CONFIG_IDPMETADATA_HOST_NAME: V1ConfigIdpMetadataHostName,
        PathValues.V1_CONFIG_IDPMETADATA: V1ConfigIdpMetadata,
        PathValues.V1_CONFIG_JWT_ISSUER_NAME: V1ConfigJwtIssuerName,
        PathValues.V1_CONFIG_JWT_ISSUER: V1ConfigJwtIssuer,
        PathValues.V1_CONFIG_JWT_NAME: V1ConfigJwtName,
        PathValues.V1_CONFIG_JWT: V1ConfigJwt,
        PathValues.V1_CONFIG_KERBEROS_REALM_REALM_NAME: V1ConfigKerberosRealmRealmName,
        PathValues.V1_CONFIG_KERBEROS_KEYTAB_PRINCIPAL_NAME: V1ConfigKerberosKeytabPrincipalName,
        PathValues.V1_CONFIG_KERBEROS_KEYTAB: V1ConfigKerberosKeytab,
        PathValues.V1_CONFIG_KERBEROS_REALM: V1ConfigKerberosRealm,
        PathValues.V1_CONFIG_LOADBALANCER_STATE: V1ConfigLoadbalancerState,
        PathValues.V1_CONFIG_LOADBALANCER_SETTINGS: V1ConfigLoadbalancerSettings,
        PathValues.V1_CONFIG_LOADBALANCER_STATS: V1ConfigLoadbalancerStats,
        PathValues.V1_MONITOR_SET_LOG_LEVELS: V1MonitorSetLogLevels,
        PathValues.V1_MONITOR_STATS: V1MonitorStats,
        PathValues.V1_MONITOR_SET_UTSERVER_LOG_LEVEL_LOG_LEVEL: V1MonitorSetUtserverLogLevelLogLevel,
        PathValues.V1_MONITOR_SEG_HEALTH_STATS: V1MonitorSegHealthStats,
        PathValues.V1_MONITOR_SEG_DIAGNOSTICS_IDENTIFIER: V1MonitorSegDiagnosticsIdentifier,
        PathValues.V1_MONITOR_SEG_CACHE_ID: V1MonitorSegCacheId,
        PathValues.V1_MONITOR_SUPPORTARCHIVE: V1MonitorSupportArchive,
        PathValues.V1_MONITOR_GET_LOG_LEVELS: V1MonitorGetLogLevels,
        PathValues.V1_MONITOR_RESET_LOG_LEVELS: V1MonitorResetLogLevels,
        PathValues.V1_CONFIG_NIC_NIC: V1ConfigNicNic,
        PathValues.V1_CONFIG_NIC: V1ConfigNic,
        PathValues.V1_CONFIG_PROXY: V1ConfigProxy,
        PathValues.V1_CONFIG_PROXY_NAME: V1ConfigProxyName,
        PathValues.V1_CONFIG_PACKAGEUPDATES: V1ConfigPackageupdates,
        PathValues.V1_CONFIG_SECURITY_AGENT_NAME: V1ConfigSecurityAgentName,
        PathValues.V1_CONFIG_SECURITY_AGENT_CONFIGURED: V1ConfigSecurityAgentConfigured,
        PathValues.V1_CONFIG_SECURITY_AGENT_AVAILABLE: V1ConfigSecurityAgentAvailable,
        PathValues.V1_CONFIG_SPEXTMETADATA_SP_EXTERNAL_HOST_NAME_INSTANCE_ID: V1ConfigSpExtMetadataSpExternalHostNameInstanceId,
        PathValues.V1_CONFIG_SPEXTMETADATA_SP_EXTERNAL_HOST_NAME: V1ConfigSpExtMetadataSpExternalHostName,
        PathValues.V1_CONFIG_SPMETADATA_NAME: V1ConfigSpMetadataName,
        PathValues.V1_CONFIG_SPMETADATA: V1ConfigSpMetadata,
        PathValues.V1_CONFIG_SETTINGS: V1ConfigSettings,
        PathValues.V1_CONFIG_CERTS_SSL_PFX_ENTITY: V1ConfigCertsSslPfxEntity,
        PathValues.V1_CONFIG_CERTS_SSL_PFX: V1ConfigCertsSslPfx,
        PathValues.V1_CONFIG_CERTS_SSL: V1ConfigCertsSsl,
        PathValues.V1_CONFIG_CERTS_SSL_ENTITY: V1ConfigCertsSslEntity,
        PathValues.V1_CONFIG_SYSLOG: V1ConfigSyslog,
        PathValues.V1_CONFIG_SYSLOG_HOST_NAME: V1ConfigSyslogHostName,
        PathValues.V1_CONFIG_SYSTEM: V1ConfigSystem,
        PathValues.V1_CONFIG_WS1INTELLIGENCEDATA: V1ConfigWs1intelligencedata,
        PathValues.V1_CONFIG_WS1INTELLIGENCE_NAME: V1ConfigWs1intelligenceName,
        PathValues.V1_CONFIG_WS1INTELLIGENCE: V1ConfigWs1intelligence,
    }
)

path_to_api = PathToApi(
    {
        PathValues.V1_CONFIG_AUTHMETHOD_SECURIDAUTH: V1ConfigAuthmethodSecuridAuth,
        PathValues.V1_CONFIG_AUTHMETHOD_CERTIFICATEAUTH: V1ConfigAuthmethodCertificateAuth,
        PathValues.V1_CONFIG_AUTHMETHOD_RADIUSAUTH: V1ConfigAuthmethodRadiusAuth,
        PathValues.V1_CONFIG_ADMINUSERS: V1ConfigAdminusers,
        PathValues.V1_CONFIG_ADMINUSERS_CHANGEPASSWORD: V1ConfigAdminusersChangePassword,
        PathValues.V1_CONFIG_ADMINUSERS_LOG_ADMIN_USER_ACTION_ACTION: V1ConfigAdminusersLogAdminUserActionAction,
        PathValues.V1_CONFIG_ADMINUSERS_ID: V1ConfigAdminusersId,
        PathValues.V1_CONFIG_ADMINUSERS_PRIVILEGES_ID: V1ConfigAdminusersPrivilegesId,
        PathValues.V1_CONFIG_ADMINUSERS_SAML_AUTH: V1ConfigAdminusersSamlAuth,
        PathValues.V1_CONFIG_AUTHMETHOD_NAME: V1ConfigAuthmethodName,
        PathValues.V1_CONFIG_AUTHMETHOD_RESET_NAME: V1ConfigAuthmethodResetName,
        PathValues.V1_CONFIG_AUTHMETHOD_OCSP_FILE_NAMES: V1ConfigAuthmethodOcspFileNames,
        PathValues.V1_CONFIG_AUTHMETHOD: V1ConfigAuthmethod,
        PathValues.V1_CONFIG_AUTHMETHOD_OCSP_CERTIFICATE: V1ConfigAuthmethodOcspCertificate,
        PathValues.V1_CONFIG_AUTHMETHOD_OCSP: V1ConfigAuthmethodOcsp,
        PathValues.V1_CONFIG_CUSTOM_BRANDING_SAVE_CUSTOM_BRANDING: V1ConfigCustomBrandingSaveCustomBranding,
        PathValues.V1_CONFIG_CUSTOM_BRANDING: V1ConfigCustomBranding,
        PathValues.V1_CONFIG_DEVICEPOLICY_NAME: V1ConfigDevicepolicyName,
        PathValues.V1_CONFIG_DEVICEPOLICY_OPSWAT: V1ConfigDevicepolicyOpswat,
        PathValues.V1_CONFIG_DEVICEPOLICY_WS1INTELLIGENCE_RISK_SCORE: V1ConfigDevicepolicyWs1IntelligenceRiskScore,
        PathValues.V1_CONFIG_DEVICEPOLICY_AVAILABLE: V1ConfigDevicepolicyAvailable,
        PathValues.V1_CONFIG_DEVICEPOLICY_CONFIGURED: V1ConfigDevicepolicyConfigured,
        PathValues.V1_CONFIG_DEVICEPOLICY: V1ConfigDevicepolicy,
        PathValues.V1_CONFIG_DISCLAIMER: V1ConfigDisclaimer,
        PathValues.V1_CONFIG_EDGESERVICE_VIEW: V1ConfigEdgeserviceView,
        PathValues.V1_CONFIG_EDGESERVICE: V1ConfigEdgeservice,
        PathValues.V1_CONFIG_EDGESERVICE_EDGE_SERVICE_TYPE: V1ConfigEdgeserviceEdgeServiceType,
        PathValues.V1_CONFIG_EDGESERVICE_FIND_CONFIGURED_EDGE_SERVICES_AND_AUTH_METHODS: V1ConfigEdgeserviceFindConfiguredEdgeServicesAndAuthMethods,
        PathValues.V1_CONFIG_EDGESERVICE_EDGE_SERVICE_TYPE_INSTANCE_ID: V1ConfigEdgeserviceEdgeServiceTypeInstanceId,
        PathValues.V1_CONFIG_EDGESERVICE_AVAILABLE_HORIZON_AUTH_METHODS: V1ConfigEdgeserviceAvailableHorizonAuthMethods,
        PathValues.V1_CONFIG_EDGESERVICE_WEBREVERSEPROXY: V1ConfigEdgeserviceWebreverseproxy,
        PathValues.V1_CONFIG_EDGESERVICE_TUNNELGATEWAY: V1ConfigEdgeserviceTunnelgateway,
        PathValues.V1_CONFIG_EDGESERVICE_TUNNELPROXY: V1ConfigEdgeserviceTunnelproxy,
        PathValues.V1_CONFIG_EDGESERVICE_SEG: V1ConfigEdgeserviceSeg,
        PathValues.V1_CONFIG_EDGESERVICE_CONTENTGATEWAY: V1ConfigEdgeserviceContentgateway,
        PathValues.V1_CONFIG_FEATURE: V1ConfigFeature,
        PathValues.V1_CONFIG_RESOURCE_UPLOAD: V1ConfigResourceUpload,
        PathValues.V1_CONFIG_RESOURCE: V1ConfigResource,
        PathValues.V1_CONFIG_RESOURCE_NAME_FILE_TYPE: V1ConfigResourceNameFileType,
        PathValues.V1_CONFIG_RESOURCE_DELETE_UPLOADED_RESOURCE_NAME_FILE_TYPE: V1ConfigResourceDeleteUploadedResourceNameFileType,
        PathValues.V1_CONFIG_RESOURCE_UPLOAD_SETTINGS_SETTINGS_ID_FILE_TYPE: V1ConfigResourceUploadSettingsSettingsIdFileType,
        PathValues.V1_CONFIG_RESOURCE_DELETE_UPLOADED_RESOURCE_SETTINGS_SETTINGS_ID_FILE_TYPE: V1ConfigResourceDeleteUploadedResourceSettingsSettingsIdFileType,
        PathValues.V1_CONFIG_GENERAL: V1ConfigGeneral,
        PathValues.V1_CONFIG_IDPEXTMETADATA: V1ConfigIdpExtMetadata,
        PathValues.V1_CONFIG_IDPEXTMETADATA_ENTITY_ID_: V1ConfigIdpExtMetadataEntityID,
        PathValues.V1_CONFIG_IDPMETADATA_HOST_NAME: V1ConfigIdpMetadataHostName,
        PathValues.V1_CONFIG_IDPMETADATA: V1ConfigIdpMetadata,
        PathValues.V1_CONFIG_JWT_ISSUER_NAME: V1ConfigJwtIssuerName,
        PathValues.V1_CONFIG_JWT_ISSUER: V1ConfigJwtIssuer,
        PathValues.V1_CONFIG_JWT_NAME: V1ConfigJwtName,
        PathValues.V1_CONFIG_JWT: V1ConfigJwt,
        PathValues.V1_CONFIG_KERBEROS_REALM_REALM_NAME: V1ConfigKerberosRealmRealmName,
        PathValues.V1_CONFIG_KERBEROS_KEYTAB_PRINCIPAL_NAME: V1ConfigKerberosKeytabPrincipalName,
        PathValues.V1_CONFIG_KERBEROS_KEYTAB: V1ConfigKerberosKeytab,
        PathValues.V1_CONFIG_KERBEROS_REALM: V1ConfigKerberosRealm,
        PathValues.V1_CONFIG_LOADBALANCER_STATE: V1ConfigLoadbalancerState,
        PathValues.V1_CONFIG_LOADBALANCER_SETTINGS: V1ConfigLoadbalancerSettings,
        PathValues.V1_CONFIG_LOADBALANCER_STATS: V1ConfigLoadbalancerStats,
        PathValues.V1_MONITOR_SET_LOG_LEVELS: V1MonitorSetLogLevels,
        PathValues.V1_MONITOR_STATS: V1MonitorStats,
        PathValues.V1_MONITOR_SET_UTSERVER_LOG_LEVEL_LOG_LEVEL: V1MonitorSetUtserverLogLevelLogLevel,
        PathValues.V1_MONITOR_SEG_HEALTH_STATS: V1MonitorSegHealthStats,
        PathValues.V1_MONITOR_SEG_DIAGNOSTICS_IDENTIFIER: V1MonitorSegDiagnosticsIdentifier,
        PathValues.V1_MONITOR_SEG_CACHE_ID: V1MonitorSegCacheId,
        PathValues.V1_MONITOR_SUPPORTARCHIVE: V1MonitorSupportArchive,
        PathValues.V1_MONITOR_GET_LOG_LEVELS: V1MonitorGetLogLevels,
        PathValues.V1_MONITOR_RESET_LOG_LEVELS: V1MonitorResetLogLevels,
        PathValues.V1_CONFIG_NIC_NIC: V1ConfigNicNic,
        PathValues.V1_CONFIG_NIC: V1ConfigNic,
        PathValues.V1_CONFIG_PROXY: V1ConfigProxy,
        PathValues.V1_CONFIG_PROXY_NAME: V1ConfigProxyName,
        PathValues.V1_CONFIG_PACKAGEUPDATES: V1ConfigPackageupdates,
        PathValues.V1_CONFIG_SECURITY_AGENT_NAME: V1ConfigSecurityAgentName,
        PathValues.V1_CONFIG_SECURITY_AGENT_CONFIGURED: V1ConfigSecurityAgentConfigured,
        PathValues.V1_CONFIG_SECURITY_AGENT_AVAILABLE: V1ConfigSecurityAgentAvailable,
        PathValues.V1_CONFIG_SPEXTMETADATA_SP_EXTERNAL_HOST_NAME_INSTANCE_ID: V1ConfigSpExtMetadataSpExternalHostNameInstanceId,
        PathValues.V1_CONFIG_SPEXTMETADATA_SP_EXTERNAL_HOST_NAME: V1ConfigSpExtMetadataSpExternalHostName,
        PathValues.V1_CONFIG_SPMETADATA_NAME: V1ConfigSpMetadataName,
        PathValues.V1_CONFIG_SPMETADATA: V1ConfigSpMetadata,
        PathValues.V1_CONFIG_SETTINGS: V1ConfigSettings,
        PathValues.V1_CONFIG_CERTS_SSL_PFX_ENTITY: V1ConfigCertsSslPfxEntity,
        PathValues.V1_CONFIG_CERTS_SSL_PFX: V1ConfigCertsSslPfx,
        PathValues.V1_CONFIG_CERTS_SSL: V1ConfigCertsSsl,
        PathValues.V1_CONFIG_CERTS_SSL_ENTITY: V1ConfigCertsSslEntity,
        PathValues.V1_CONFIG_SYSLOG: V1ConfigSyslog,
        PathValues.V1_CONFIG_SYSLOG_HOST_NAME: V1ConfigSyslogHostName,
        PathValues.V1_CONFIG_SYSTEM: V1ConfigSystem,
        PathValues.V1_CONFIG_WS1INTELLIGENCEDATA: V1ConfigWs1intelligencedata,
        PathValues.V1_CONFIG_WS1INTELLIGENCE_NAME: V1ConfigWs1intelligenceName,
        PathValues.V1_CONFIG_WS1INTELLIGENCE: V1ConfigWs1intelligence,
    }
)
