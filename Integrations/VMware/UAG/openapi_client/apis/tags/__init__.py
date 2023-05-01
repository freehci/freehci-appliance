# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from openapi_client.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    ADMIN_USER_SETTINGS = "AdminUserSettings"
    AUTH_METHOD_SETTINGS = "AuthMethodSettings"
    CUSTOM_BRANDING = "CustomBranding"
    DEVICE_POLICY_SETTINGS = "DevicePolicySettings"
    ADMIN_DISCLAIMER_TEXT = "Admin Disclaimer Text"
    EDGE_SERVICE_SETTINGS = "EdgeServiceSettings"
    UAGFEATURE_SETTINGS = "UAGFeatureSettings"
    FILE_UPLOAD_SETTINGS = "FileUploadSettings"
    GENERAL_SETTINGS = "GeneralSettings"
    IDENTITY_PROVIDER_EXTERNAL_METADATA = "IdentityProviderExternalMetadata"
    IDENTITY_PROVIDER_METADATA = "IdentityProviderMetadata"
    JWTISSUER_SETTINGS = "JWTIssuerSettings"
    JWTSETTINGS = "JWTSettings"
    KERBEROS_SETTINGS = "KerberosSettings"
    LOAD_BALANCER_SETTINGS = "LoadBalancerSettings"
    LOG_OPERATIONS = "LogOperations"
    NIC_SETTINGS = "NicSettings"
    OUTBOUND_PROXY_SETTINGS = "Outbound ProxySettings"
    PACKAGE_UPDATE_SETTINGS = "PackageUpdateSettings"
    SECURITY_AGENT_SETTINGS = "SecurityAgentSettings"
    SERVICE_PROVIDER_EXTERNAL_METADATA_RESOURCE = "ServiceProviderExternalMetadataResource"
    SERVICE_PROVIDER_METADATA = "ServiceProviderMetadata"
    UAGSETTINGS = "UAGSettings"
    SERVER_CERTIFICATE = "ServerCertificate"
    SYSLOG_SERVER_SETTINGS = "Syslog server Settings"
    SYSTEM_SETTINGS = "SystemSettings"
    WORKSPACE_ONE_INTELLIGENCE_DATA_SETTINGS = "WorkspaceOneIntelligenceDataSettings"
    WORKSPACE_ONE_INTELLIGENCE_SETTINGS = "WorkspaceOneIntelligenceSettings"
