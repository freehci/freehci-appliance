# openapi_client.model.nic_settings.NicSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**allocationMode** | str,  | str,  | The IP allocation mode. | must be one of ["STATICV4", "STATICV6", "DHCPV4", "DHCPV6", "AUTOV6", "STATICV4_STATICV6", "STATICV4_DHCPV6", "STATICV4_AUTOV6", "DHCPV4_STATICV6", "DHCPV4_DHCPV6", "DHCPV4_AUTOV6", "Static", "Dynamic", ] 
**ipv4Address** | str,  | str,  | New IPV4 address for the Nic. | 
**ipv4Netmask** | str,  | str,  | New IPV4 netmask for the Nic. | 
**nic** | str,  | str,  | The NIC identifier, can have value eth0,eth1,eth2 based on VM configuration selected | must be one of ["eth0", "eth1", "eth2", ] 
**ipv4DefaultGateway** | str,  | str,  | New IPV4 default gateway | [optional] 
**ipv4StaticRoutes** | str,  | str,  | The IPV4 static routes to be defined for this NIC. Comma separated list of routes in the form ipv4-network-address/bits ipv4-gateway address or ipv4-network-address/bits eg: 20.2.0.0/16 10.2.0.1, 30.2.0.0/16 | [optional] 
**customConfig** | str,  | str,  | Custom configuration to apply in .network files of given nic. Formatted as SectionName^Parameter&#x3D;Value;. Refer: https://man7.org/linux/man-pages/man5/systemd.network.5.html | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

