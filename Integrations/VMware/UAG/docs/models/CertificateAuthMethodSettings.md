# openapi_client.model.certificate_auth_method_settings.CertificateAuthMethodSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**enableOCSP** | bool,  | BoolClass,  | Enable OCSP Revocation | 
**validateUpn** | bool,  | BoolClass,  | Validate UPN Format | 
**caCertificates** | str,  | str,  | Trusted CA certificates in PEM format. | 
**sendOCSPNonce** | bool,  | BoolClass,  | Send OCSP Nonce | 
**enableCertCRL** | bool,  | BoolClass,  | Use CRL from Certificates | 
**enabled** | bool,  | BoolClass,  | Enable Certificate Adapter | 
**enableOCSPCRLFailover** | bool,  | BoolClass,  | Use CRL in case of OCSP failure | 
**ocspURLSource** | str,  | str,  | OCSP URL Source | must be one of ["config_only", "cert_only_optional", "cert_only_required", "cert_and_config", ] 
**enableConsentForm** | bool,  | BoolClass,  | Enable Consent Form before Authentication | 
**ocspURL** | str,  | str,  | OCSP URL | 
**enableCertRevocation** | bool,  | BoolClass,  | Enable Cert Revocation | 
**certificatePolicies** | str,  | str,  | Certificate Policies Accepted | 
**consentForm** | str,  | str,  | Consent Form Content | 
**name** | str,  | str,  | The name of the authentication method. | 
**userIdSource** | str,  | str,  | User Identifier Search Order | must be one of ["email", "subject", "upn", "email.subject", "email.upn", "subject.email", "subject.upn", "upn.email", "upn.subject", "email.subject.upn", "email.upn.subject", "subject.email.upn", "subject.upn.email", "upn.email.subject", "upn.subject.email", ] 
**crlLocation** | str,  | str,  | CRL Location | 
**requestTimeout** | str,  | str,  | Request Timeout | 
**className** | str,  | str,  | The name of the class that implements the authentication method. | [optional] 
**displayName** | str,  | str,  | The name of the method useful for display to the user. | [optional] 
**jarFile** | str,  | str,  | The path name of the JAR file that contains the authentication method. | [optional] 
**authMethod** | str,  | str,  | The formal name (URN) of the authentication method. | [optional] 
**versionNum** | str,  | str,  | The version of the authentication method. | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

