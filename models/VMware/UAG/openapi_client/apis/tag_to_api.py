import typing_extensions

from openapi_client.apis.tags import TagValues
from openapi_client.apis.tags.admin_user_settings_api import AdminUserSettingsApi
from openapi_client.apis.tags.auth_method_settings_api import AuthMethodSettingsApi
from openapi_client.apis.tags.custom_branding_api import CustomBrandingApi
from openapi_client.apis.tags.device_policy_settings_api import DevicePolicySettingsApi
from openapi_client.apis.tags.admin_disclaimer_text_api import AdminDisclaimerTextApi
from openapi_client.apis.tags.edge_service_settings_api import EdgeServiceSettingsApi
from openapi_client.apis.tags.uag_feature_settings_api import UAGFeatureSettingsApi
from openapi_client.apis.tags.file_upload_settings_api import FileUploadSettingsApi
from openapi_client.apis.tags.general_settings_api import GeneralSettingsApi
from openapi_client.apis.tags.identity_provider_external_metadata_api import IdentityProviderExternalMetadataApi
from openapi_client.apis.tags.identity_provider_metadata_api import IdentityProviderMetadataApi
from openapi_client.apis.tags.jwt_issuer_settings_api import JWTIssuerSettingsApi
from openapi_client.apis.tags.jwt_settings_api import JWTSettingsApi
from openapi_client.apis.tags.kerberos_settings_api import KerberosSettingsApi
from openapi_client.apis.tags.load_balancer_settings_api import LoadBalancerSettingsApi
from openapi_client.apis.tags.log_operations_api import LogOperationsApi
from openapi_client.apis.tags.nic_settings_api import NicSettingsApi
from openapi_client.apis.tags.outbound_proxy_settings_api import OutboundProxySettingsApi
from openapi_client.apis.tags.package_update_settings_api import PackageUpdateSettingsApi
from openapi_client.apis.tags.security_agent_settings_api import SecurityAgentSettingsApi
from openapi_client.apis.tags.service_provider_external_metadata_resource_api import ServiceProviderExternalMetadataResourceApi
from openapi_client.apis.tags.service_provider_metadata_api import ServiceProviderMetadataApi
from openapi_client.apis.tags.uag_settings_api import UAGSettingsApi
from openapi_client.apis.tags.server_certificate_api import ServerCertificateApi
from openapi_client.apis.tags.syslog_server_settings_api import SyslogServerSettingsApi
from openapi_client.apis.tags.system_settings_api import SystemSettingsApi
from openapi_client.apis.tags.workspace_one_intelligence_data_settings_api import WorkspaceOneIntelligenceDataSettingsApi
from openapi_client.apis.tags.workspace_one_intelligence_settings_api import WorkspaceOneIntelligenceSettingsApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.ADMIN_USER_SETTINGS: AdminUserSettingsApi,
        TagValues.AUTH_METHOD_SETTINGS: AuthMethodSettingsApi,
        TagValues.CUSTOM_BRANDING: CustomBrandingApi,
        TagValues.DEVICE_POLICY_SETTINGS: DevicePolicySettingsApi,
        TagValues.ADMIN_DISCLAIMER_TEXT: AdminDisclaimerTextApi,
        TagValues.EDGE_SERVICE_SETTINGS: EdgeServiceSettingsApi,
        TagValues.UAGFEATURE_SETTINGS: UAGFeatureSettingsApi,
        TagValues.FILE_UPLOAD_SETTINGS: FileUploadSettingsApi,
        TagValues.GENERAL_SETTINGS: GeneralSettingsApi,
        TagValues.IDENTITY_PROVIDER_EXTERNAL_METADATA: IdentityProviderExternalMetadataApi,
        TagValues.IDENTITY_PROVIDER_METADATA: IdentityProviderMetadataApi,
        TagValues.JWTISSUER_SETTINGS: JWTIssuerSettingsApi,
        TagValues.JWTSETTINGS: JWTSettingsApi,
        TagValues.KERBEROS_SETTINGS: KerberosSettingsApi,
        TagValues.LOAD_BALANCER_SETTINGS: LoadBalancerSettingsApi,
        TagValues.LOG_OPERATIONS: LogOperationsApi,
        TagValues.NIC_SETTINGS: NicSettingsApi,
        TagValues.OUTBOUND_PROXY_SETTINGS: OutboundProxySettingsApi,
        TagValues.PACKAGE_UPDATE_SETTINGS: PackageUpdateSettingsApi,
        TagValues.SECURITY_AGENT_SETTINGS: SecurityAgentSettingsApi,
        TagValues.SERVICE_PROVIDER_EXTERNAL_METADATA_RESOURCE: ServiceProviderExternalMetadataResourceApi,
        TagValues.SERVICE_PROVIDER_METADATA: ServiceProviderMetadataApi,
        TagValues.UAGSETTINGS: UAGSettingsApi,
        TagValues.SERVER_CERTIFICATE: ServerCertificateApi,
        TagValues.SYSLOG_SERVER_SETTINGS: SyslogServerSettingsApi,
        TagValues.SYSTEM_SETTINGS: SystemSettingsApi,
        TagValues.WORKSPACE_ONE_INTELLIGENCE_DATA_SETTINGS: WorkspaceOneIntelligenceDataSettingsApi,
        TagValues.WORKSPACE_ONE_INTELLIGENCE_SETTINGS: WorkspaceOneIntelligenceSettingsApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.ADMIN_USER_SETTINGS: AdminUserSettingsApi,
        TagValues.AUTH_METHOD_SETTINGS: AuthMethodSettingsApi,
        TagValues.CUSTOM_BRANDING: CustomBrandingApi,
        TagValues.DEVICE_POLICY_SETTINGS: DevicePolicySettingsApi,
        TagValues.ADMIN_DISCLAIMER_TEXT: AdminDisclaimerTextApi,
        TagValues.EDGE_SERVICE_SETTINGS: EdgeServiceSettingsApi,
        TagValues.UAGFEATURE_SETTINGS: UAGFeatureSettingsApi,
        TagValues.FILE_UPLOAD_SETTINGS: FileUploadSettingsApi,
        TagValues.GENERAL_SETTINGS: GeneralSettingsApi,
        TagValues.IDENTITY_PROVIDER_EXTERNAL_METADATA: IdentityProviderExternalMetadataApi,
        TagValues.IDENTITY_PROVIDER_METADATA: IdentityProviderMetadataApi,
        TagValues.JWTISSUER_SETTINGS: JWTIssuerSettingsApi,
        TagValues.JWTSETTINGS: JWTSettingsApi,
        TagValues.KERBEROS_SETTINGS: KerberosSettingsApi,
        TagValues.LOAD_BALANCER_SETTINGS: LoadBalancerSettingsApi,
        TagValues.LOG_OPERATIONS: LogOperationsApi,
        TagValues.NIC_SETTINGS: NicSettingsApi,
        TagValues.OUTBOUND_PROXY_SETTINGS: OutboundProxySettingsApi,
        TagValues.PACKAGE_UPDATE_SETTINGS: PackageUpdateSettingsApi,
        TagValues.SECURITY_AGENT_SETTINGS: SecurityAgentSettingsApi,
        TagValues.SERVICE_PROVIDER_EXTERNAL_METADATA_RESOURCE: ServiceProviderExternalMetadataResourceApi,
        TagValues.SERVICE_PROVIDER_METADATA: ServiceProviderMetadataApi,
        TagValues.UAGSETTINGS: UAGSettingsApi,
        TagValues.SERVER_CERTIFICATE: ServerCertificateApi,
        TagValues.SYSLOG_SERVER_SETTINGS: SyslogServerSettingsApi,
        TagValues.SYSTEM_SETTINGS: SystemSettingsApi,
        TagValues.WORKSPACE_ONE_INTELLIGENCE_DATA_SETTINGS: WorkspaceOneIntelligenceDataSettingsApi,
        TagValues.WORKSPACE_ONE_INTELLIGENCE_SETTINGS: WorkspaceOneIntelligenceSettingsApi,
    }
)
