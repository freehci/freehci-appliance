# openapi_client.model.system_settings.SystemSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**coreDumpSettings** | [**CoreDumpSettings**](CoreDumpSettings.md) | [**CoreDumpSettings**](CoreDumpSettings.md) |  | 
**fipsEnabled** | bool,  | BoolClass,  | This is a read-only property to indicate that this access point is FIPS compliant/non-compliant | [optional] 
**adminPasswordExpirationDays** | decimal.Decimal, int,  | decimal.Decimal,  | The expiration time for admin password (in days) | [optional] value must be a 32 bit integer
**adminSessionIdleTimeoutMinutes** | decimal.Decimal, int,  | decimal.Decimal,  | The idle timeout for admin user authenticated sessions | [optional] value must be a 32 bit integer
**adminMaxConcurrentSessions** | decimal.Decimal, int,  | decimal.Decimal,  | Maximum concurrent logged in sessions for remote admin users | [optional] value must be a 32 bit integer
**rootPasswordExpirationDays** | decimal.Decimal, int,  | decimal.Decimal,  | Root Password Expiration Days | [optional] value must be a 32 bit integer
**rootSessionIdleTimeoutSeconds** | decimal.Decimal, int,  | decimal.Decimal,  | The idle timeout for root authenticated sessions | [optional] value must be a 32 bit integer
**osLoginUsername** | str,  | str,  | Non-root user for UAG local console login configurable at deploy time. If this is configured, root access will be disabled | [optional] 
**osMaxLoginLimit** | str,  | str,  | Maximum concurrent session limit for sudo user. This field is ignored if sudo user is not configured | [optional] 
**monitoringUsersPasswordExpirationDays** | decimal.Decimal, int,  | decimal.Decimal,  | The expiration time for monitoring Users password (in days). | [optional] value must be a 32 bit integer
**adminPasswordPolicySettings** | [**PasswordPolicySettings**](PasswordPolicySettings.md) | [**PasswordPolicySettings**](PasswordPolicySettings.md) |  | [optional] 
**passwordPolicySettings** | [**PasswordPolicySettings**](PasswordPolicySettings.md) | [**PasswordPolicySettings**](PasswordPolicySettings.md) |  | [optional] 
**cipherSuites** | str,  | str,  | The set of SSL/TLS cipher suites to be enabled for inbound connections. Format: a comma separated list of cipher suite names. If not set, a default list is used. | [optional] 
**outboundCipherSuites** | str,  | str,  | The set of TLS cipher suites for outbound connections from UAG. Format: a comma separated list of cipher suite params. If not set, underlying SSL provider will present its default list of ciphers during ClientHello to the remote server | [optional] 
**sslProvider** | str,  | str,  | SSL provider for ESManager connections. Permissible values are JDK &amp; OPENSSL (default). | [optional] must be one of ["JDK", "OPENSSL", "OPENSSL_REFCNT", ] 
**tlsNamedGroups** | str,  | str,  | Elliptic curves that are allowed for use under Supported_groups extension during TLS handshake. Currently this configuration is supported only when sslProvider is set to JDK. | [optional] 
**tlsSignatureSchemes** | str,  | str,  | Signature Schemes that are allowed for use under Signature Algorithms extension duringTLS handshake. Currently this configuration is supported only when sslProvider is set to JDK. | [optional] 
**ssl30Enabled** | bool,  | BoolClass,  | SSL 3.0 enabled. | [optional] 
**tls10Enabled** | bool,  | BoolClass,  | TLS 1.0 enabled. | [optional] 
**tls11Enabled** | bool,  | BoolClass,  | TLS 1.1 enabled. | [optional] 
**tls12Enabled** | bool,  | BoolClass,  | TLS 1.2 enabled. | [optional] 
**tls13Enabled** | bool,  | BoolClass,  | TLS 1.3 enabled. | [optional] 
**adminDisclaimerText** | str,  | str,  | Update Admin disclaimer text. | [optional] 
**syslogUrl** | str,  | str,  | Overrides the default syslog server/port Format is [syslog://]hostname[:port]. Default value (localhost)  will be used if not set. | [optional] 
**syslogAuditUrl** | str,  | str,  | Overrides the default syslogAudit server/port Format is [syslog://]hostname[:port]. Default value (localhost)  will be used if not set. | [optional] 
**sysLogType** | str,  | str,  | Type of communication to be used for syslog server. Valid values [UDP, TCP, TLS] | [optional] must be one of ["UDP", "TCP", "TLS", "MQTT", ] 
**syslogServerCACertPem** | str,  | str,  | CA certificate of the syslog server in PEM format. Mandatory field if syslog type is TLS | [optional] 
**syslogClientCertCertPem** | str,  | str,  | Client certificate in PEM format. To be used during TLS communicationwith syslog server. Only provide if syslog server needs mutual (client-cert) authentication | [optional] 
**syslogClientCertKeyPem** | str,  | str,  | Client certificate Private key in PEM format. Only provide if syslog server needs mutual (client-cert) authentication | [optional] 
**[tlsSyslogServerSettings](#tlsSyslogServerSettings)** | list, tuple,  | tuple,  | List of syslog server settings. Used in TLS mode | [optional] 
**healthCheckUrl** | str,  | str,  | Health check url to be used. Default is /favicon.ico | [optional] 
**enableHTTPHealthMonitor** | bool,  | BoolClass,  | Controls if health check should respond on port 80 or not. By default we will not send response on port 80 for health check requests | [optional] 
**cookiesToBeCached** | str,  | str,  | Set of cookies to be cached by AP | [optional] 
**ipMode** | str,  | str,  | Indicates the mode of UAG for NIC 1 (eth0) | [optional] must be one of ["STATICV4", "STATICV6", "DHCPV4", "DHCPV6", "AUTOV6", "STATICV4_STATICV6", "STATICV4_DHCPV6", "STATICV4_AUTOV6", "DHCPV4_STATICV6", "DHCPV4_DHCPV6", "DHCPV4_AUTOV6", "Static", "Dynamic", ] 
**ipModeforNIC2** | str,  | str,  | Indicates the mode of UAG for NIC 2 (eth1) | [optional] must be one of ["STATICV4", "STATICV6", "DHCPV4", "DHCPV6", "AUTOV6", "STATICV4_STATICV6", "STATICV4_DHCPV6", "STATICV4_AUTOV6", "DHCPV4_STATICV6", "DHCPV4_DHCPV6", "DHCPV4_AUTOV6", "Static", "Dynamic", ] 
**ipModeforNIC3** | str,  | str,  | Indicates the mode of UAG for NIC 3 (eth2) | [optional] must be one of ["STATICV4", "STATICV6", "DHCPV4", "DHCPV6", "AUTOV6", "STATICV4_STATICV6", "STATICV4_DHCPV6", "STATICV4_AUTOV6", "DHCPV4_STATICV6", "DHCPV4_DHCPV6", "DHCPV4_AUTOV6", "Static", "Dynamic", ] 
**defaultRedirectHost** | str,  | str,  |  | [optional] 
**sessionTimeout** | decimal.Decimal, int,  | decimal.Decimal,  | Session timeout in milliseconds. Set by default to 10 hours | [optional] value must be a 64 bit integer
**requestTimeoutMsec** | decimal.Decimal, int,  | decimal.Decimal,  | maximum time in seconds to wait for a request to be received | [optional] value must be a 64 bit integer
**bodyReceiveTimeoutMsec** | decimal.Decimal, int,  | decimal.Decimal,  | maximum time in seconds to wait for a request body to be received | [optional] value must be a 64 bit integer
**authenticationTimeout** | decimal.Decimal, int,  | decimal.Decimal,  | maximum wait time in seconds before which authentication must happen | [optional] value must be a 64 bit integer
**quiesceMode** | bool,  | BoolClass,  | quiesce mode | [optional] 
**monitorInterval** | decimal.Decimal, int,  | decimal.Decimal,  | This is for monitoring AP | [optional] value must be a 32 bit integer
**samlCertRolloverSupported** | bool,  | BoolClass,  | Certificate rollover support for SAML authentication by generating certificate linked SAML SP metadata. If enabled, IDP needs to be reconfigured when TLS certificate is updated in UAG. | [optional] 
**httpConnectionTimeout** | decimal.Decimal, int,  | decimal.Decimal,  | Timeout to wait for connection attempt to succeed. This will also be the response read timeout(Default value is 120 seconds) | [optional] value must be a 32 bit integer
**tlsPortSharingEnabled** | bool,  | BoolClass,  | Enable HAProxy for TLS port sharing | [optional] 
**uagName** | str,  | str,  | Name assigned to the UAG appliance | [optional] 
**ceipEnabled** | bool,  | BoolClass,  | Enable/disable posting CEIP data to VMware | [optional] 
**adminCertRolledBack** | bool,  | BoolClass,  | A read-only property to indicate if uploaded certificate on Admin interface was successful or it was rolled back to a generated self-signed cert | [optional] 
**clientConnectionIdleTimeout** | decimal.Decimal, int,  | decimal.Decimal,  | Indicates the time (in seconds) a client connection can stay idle before the connection will be closed. Default value is 360 seconds (6 minutes).A value of Zero means infinite time i.e no idle timeout | [optional] value must be a 32 bit integer
**sshEnabled** | bool,  | BoolClass,  |  | [optional] 
**sshPasswordAccessEnabled** | bool,  | BoolClass,  |  | [optional] 
**sshKeyAccessEnabled** | bool,  | BoolClass,  |  | [optional] 
**sshInterface** | str,  | str,  |  | [optional] 
**sshPort** | str,  | str,  |  | [optional] 
**sshLoginBannerText** | str,  | str,  |  | [optional] 
**[sshPublicKeys](#sshPublicKeys)** | list, tuple,  | tuple,  |  | [optional] 
**dns** | str,  | str,  | DNS server addresses | [optional] 
**dnsSearch** | str,  | str,  | DNS search list | [optional] 
**snmpEnabled** | bool,  | BoolClass,  | SNMP service enabled or disabled | [optional] 
**snmpSettings** | [**SnmpSettings**](SnmpSettings.md) | [**SnmpSettings**](SnmpSettings.md) |  | [optional] 
**hostClockSyncSupported** | bool,  | BoolClass,  | Flag to indicate if the Clock sync with virtualization host is supported | [optional] 
**hostClockSyncEnabled** | bool,  | BoolClass,  | Flag to indicate if the Clock sync with virtualization host is enabled | [optional] 
**ntpServers** | str,  | str,  | Primary NTP servers to configure for time sync. Space separated list | [optional] 
**fallBackNtpServers** | str,  | str,  | Fallback NTP servers to configure for time sync. Space separated list | [optional] 
**clockSkewTolerance** | decimal.Decimal, int,  | decimal.Decimal,  | The clock skew tolerance (in secs) in UAG. Default value is 10 mins | [optional] value must be a 32 bit integer
**maxConnectionsAllowedPerSession** | decimal.Decimal, int,  | decimal.Decimal,  | Maximum parallel input connections per session. Make it zero for ignoring limit | [optional] value must be a 32 bit integer
**maxSystemCPUAllowed** | decimal.Decimal, int,  | decimal.Decimal,  | Maximum allowed System CPU limit. After this system CPU average over past 1 minute reaches this limit no new sessions will be allowed. UAG will start sending 503 responses for new session requests | [optional] value must be a 32 bit integer
**allowedHostHeaderValues** | str,  | str,  | Comma separated list of all allowed hostnames. If non empty then incoming host header should match one of the host name in the listIf empty then host name header wont be validated | [optional] 
**enabledAdvancedFeatures** | str,  | str,  |  | [optional] 
**secureRandomSource** | str,  | str,  |  | [optional] 
**forcedRestart** | bool,  | BoolClass,  |  | [optional] 
**extendedServerCertValidationEnabled** | bool,  | BoolClass,  |  | [optional] 
**commandsFirstBoot** | str,  | str,  | List of shell commands separated by semi-colon that run only during the first boot of UAG. Maximum length is 8kB | [optional] 
**commandsEveryBoot** | str,  | str,  | List of shell commands separated by semi-colon that run during the every boot up of UAG.  Maximum length is 8kB | [optional] 
**dsComplianceOS** | bool,  | BoolClass,  |  | [optional] 
**unrecognizedSessionsMonitoringEnabled** | bool,  | BoolClass,  |  | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

# tlsSyslogServerSettings

List of syslog server settings. Used in TLS mode

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  | List of syslog server settings. Used in TLS mode | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**TlsSyslogServerSettings**](TlsSyslogServerSettings.md) | [**TlsSyslogServerSettings**](TlsSyslogServerSettings.md) | [**TlsSyslogServerSettings**](TlsSyslogServerSettings.md) |  | 

# sshPublicKeys

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
list, tuple,  | tuple,  |  | 

### Tuple Items
Class Name | Input Type | Accessed Type | Description | Notes
------------- | ------------- | ------------- | ------------- | -------------
[**SshPublicKey**](SshPublicKey.md) | [**SshPublicKey**](SshPublicKey.md) | [**SshPublicKey**](SshPublicKey.md) |  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

