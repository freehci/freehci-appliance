# openapi_client.model.settings.Settings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**generalSettings** | [**GeneralSettings**](GeneralSettings.md) | [**GeneralSettings**](GeneralSettings.md) |  | [optional] 
**systemSettings** | [**SystemSettings**](SystemSettings.md) | [**SystemSettings**](SystemSettings.md) |  | [optional] 
**edgeServiceSettingsList** | [**EdgeServiceSettingsList**](EdgeServiceSettingsList.md) | [**EdgeServiceSettingsList**](EdgeServiceSettingsList.md) |  | [optional] 
**authMethodSettingsList** | [**AuthMethodSettingsList**](AuthMethodSettingsList.md) | [**AuthMethodSettingsList**](AuthMethodSettingsList.md) |  | [optional] 
**kerberosKeyTabSettingsList** | [**KerberosKeyTabSettingsList**](KerberosKeyTabSettingsList.md) | [**KerberosKeyTabSettingsList**](KerberosKeyTabSettingsList.md) |  | [optional] 
**kerberosRealmSettingsList** | [**KerberosRealmSettingsList**](KerberosRealmSettingsList.md) | [**KerberosRealmSettingsList**](KerberosRealmSettingsList.md) |  | [optional] 
**certificateWrapper** | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) |  | [optional] 
**certificateWrapperAdmin** | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) |  | [optional] 
**serviceProviderMetadataList** | [**SpMediaTypes**](SpMediaTypes.md) | [**SpMediaTypes**](SpMediaTypes.md) |  | [optional] 
**identityProviderMetaData** | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) | [**CertificateChainAndKeyWrapper**](CertificateChainAndKeyWrapper.md) |  | [optional] 
**pfxCertStoreWrapper** | [**PfxCertStoreWrapper**](PfxCertStoreWrapper.md) | [**PfxCertStoreWrapper**](PfxCertStoreWrapper.md) |  | [optional] 
**pfxCertStoreWrapperAdmin** | [**PfxCertStoreWrapper**](PfxCertStoreWrapper.md) | [**PfxCertStoreWrapper**](PfxCertStoreWrapper.md) |  | [optional] 
**idpMediaType** | [**IdpMediaType**](IdpMediaType.md) | [**IdpMediaType**](IdpMediaType.md) |  | [optional] 
**customBrandingSettings** | [**CustomBrandingSettings**](CustomBrandingSettings.md) | [**CustomBrandingSettings**](CustomBrandingSettings.md) |  | [optional] 
**idPExternalMetadataSettingsList** | [**IdPExternalMetadataSettingsList**](IdPExternalMetadataSettingsList.md) | [**IdPExternalMetadataSettingsList**](IdPExternalMetadataSettingsList.md) |  | [optional] 
**devicePolicySettingsList** | [**DevicePolicySettingsList**](DevicePolicySettingsList.md) | [**DevicePolicySettingsList**](DevicePolicySettingsList.md) |  | [optional] 
**loadBalancerSettings** | [**LoadBalancerSettings**](LoadBalancerSettings.md) | [**LoadBalancerSettings**](LoadBalancerSettings.md) |  | [optional] 
**jwtSettingsList** | [**JWTSettingsList**](JWTSettingsList.md) | [**JWTSettingsList**](JWTSettingsList.md) |  | [optional] 
**jwtIssuerSettingsList** | [**JWTIssuerSettingsList**](JWTIssuerSettingsList.md) | [**JWTIssuerSettingsList**](JWTIssuerSettingsList.md) |  | [optional] 
**workspaceOneIntelligenceSettingsList** | [**WS1IntelligenceSettingsList**](WS1IntelligenceSettingsList.md) | [**WS1IntelligenceSettingsList**](WS1IntelligenceSettingsList.md) |  | [optional] 
**workspaceOneIntelligenceDataSettings** | [**WorkspaceOneIntelligenceDataSettings**](WorkspaceOneIntelligenceDataSettings.md) | [**WorkspaceOneIntelligenceDataSettings**](WorkspaceOneIntelligenceDataSettings.md) |  | [optional] 
**outboundProxySettingsList** | [**OutboundProxySettingsList**](OutboundProxySettingsList.md) | [**OutboundProxySettingsList**](OutboundProxySettingsList.md) |  | [optional] 
**ocspSigningCertList** | [**OCSPSigningCertList**](OCSPSigningCertList.md) | [**OCSPSigningCertList**](OCSPSigningCertList.md) |  | [optional] 
**packageUpdatesSettings** | [**PackageUpdateSettings**](PackageUpdateSettings.md) | [**PackageUpdateSettings**](PackageUpdateSettings.md) |  | [optional] 
**adminUsersList** | [**AdminUsersList**](AdminUsersList.md) | [**AdminUsersList**](AdminUsersList.md) |  | [optional] 
**customExecutableList** | [**CustomExecutableList**](CustomExecutableList.md) | [**CustomExecutableList**](CustomExecutableList.md) |  | [optional] 
**syslogSettings** | [**SyslogSettings**](SyslogSettings.md) | [**SyslogSettings**](SyslogSettings.md) |  | [optional] 
**adminSAMLSettings** | [**AdminSAMLSettings**](AdminSAMLSettings.md) | [**AdminSAMLSettings**](AdminSAMLSettings.md) |  | [optional] 
**securityAgentSettingsList** | [**SecurityAgentSettingsList**](SecurityAgentSettingsList.md) | [**SecurityAgentSettingsList**](SecurityAgentSettingsList.md) |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

