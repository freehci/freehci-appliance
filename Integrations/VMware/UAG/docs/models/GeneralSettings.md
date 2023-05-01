# openapi_client.model.general_settings.GeneralSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**name** | str,  | str,  | Name of UAG appliance | [optional] 
**source** | str,  | str,  | Path of OVA file | [optional] 
**target** | str,  | str,  | Location in vCenter server, where UAG instance is deployed | [optional] 
**ds** | str,  | str,  | vSphere data store name | [optional] 
**diskMode** | str,  | str,  | vSphere disk provisioning mode | [optional] 
**netInternet** | str,  | str,  | vSphere Internet facing network name | [optional] 
**netManagementNetwork** | str,  | str,  | vSphere network name for management network, which hosts the administrative REST API | [optional] 
**netBackendNetwork** | str,  | str,  | vSphere network to route traffic to backend services | [optional] 
**ipMode0** | str,  | str,  | IP Address mode for NIC 1 | [optional] 
**ipMode1** | str,  | str,  | IP Address mode for NIC 2 | [optional] 
**ipMode2** | str,  | str,  | IP Address mode for NIC 3 | [optional] 
**ip0** | str,  | str,  | NIC 1 (eth0) IPv4 address | [optional] 
**eth0ErrorMsg** | str,  | str,  | NIC 1 (eth0) error msg during update. | [optional] 
**eth0CustomConfig** | str,  | str,  | Custom configuration to apply in .network files of given nic. Formatted as SectionName^Parameter&#x3D;Value;. Refer: https://man7.org/linux/man-pages/man5/systemd.network.5.html | [optional] 
**routes0** | str,  | str,  | Comma separated list of IPv4 custom routes for NIC 1 (eth0) in the form ipv4-network-address/bits ipv4-gateway-address | [optional] 
**netmask0** | str,  | str,  | Internet Netmask | [optional] 
**gateway0** | str,  | str,  | Internet Default Gateway | [optional] 
**forceNetmask0** | str,  | str,  | Internet Netmask | [optional] 
**forceIpv6Prefix0** | str,  | str,  | Internet Netmask | [optional] 
**ip0AllocationMode** | str,  | str,  | IP Allocation Mode for NIC 1 | [optional] must be one of ["STATICV4", "STATICV6", "DHCPV4", "DHCPV6", "AUTOV6", "STATICV4_STATICV6", "STATICV4_DHCPV6", "STATICV4_AUTOV6", "DHCPV4_STATICV6", "DHCPV4_DHCPV6", "DHCPV4_AUTOV6", "Static", "Dynamic", ] 
**defaultGateway** | str,  | str,  | The default gateway address | [optional] 
**v6DefaultGateway** | str,  | str,  | The default IPv6 gateway address | [optional] 
**ip1** | str,  | str,  | NIC 2 (eth1) IPv4 address | [optional] 
**eth1ErrorMsg** | str,  | str,  | NIC 2 (eth1) error msg during update. | [optional] 
**eth1CustomConfig** | str,  | str,  | Custom configuration to apply in .network files of given nic. Formatted as SectionName^Parameter&#x3D;Value;. Refer: https://man7.org/linux/man-pages/man5/systemd.network.5.html | [optional] 
**routes1** | str,  | str,  | Comma separated list of IPv4 custom routes for NIC 2 (eth1) in the form ipv4-network-address/bits ipv4-gateway-address | [optional] 
**netmask1** | str,  | str,  | Management Network Netmask | [optional] 
**gateway1** | str,  | str,  | Management Network Default Gateway | [optional] 
**forceNetmask1** | str,  | str,  | Overriding Management Netmask | [optional] 
**forceIpv6Prefix1** | str,  | str,  | Management Netmask | [optional] 
**ip1AllocationMode** | str,  | str,  | IP Allocation Mode | [optional] must be one of ["STATICV4", "STATICV6", "DHCPV4", "DHCPV6", "AUTOV6", "STATICV4_STATICV6", "STATICV4_DHCPV6", "STATICV4_AUTOV6", "DHCPV4_STATICV6", "DHCPV4_DHCPV6", "DHCPV4_AUTOV6", "Static", "Dynamic", ] 
**ip2** | str,  | str,  | NIC 3 (eth2) IPv4 address | [optional] 
**eth2ErrorMsg** | str,  | str,  | NIC 3 (eth2) error msg during update. | [optional] 
**eth2CustomConfig** | str,  | str,  | Custom configuration to apply in .network files of given nic. Formatted as SectionName^Parameter&#x3D;Value;. Refer: https://man7.org/linux/man-pages/man5/systemd.network.5.html | [optional] 
**routes2** | str,  | str,  | Comma separated list of IPv4 custom routes for NIC 3 (eth2) in the form ipv4-network-address/bits ipv4-gateway-address | [optional] 
**netmask2** | str,  | str,  | Backend Network Netmask | [optional] 
**gateway2** | str,  | str,  | Backend Network Default Gateway | [optional] 
**forceNetmask2** | str,  | str,  | Overriding Backend Netmask | [optional] 
**forceIpv6Prefix2** | str,  | str,  | Backend Netmask | [optional] 
**ip2AllocationMode** | str,  | str,  | IP Allocation Mode | [optional] must be one of ["STATICV4", "STATICV6", "DHCPV4", "DHCPV6", "AUTOV6", "STATICV4_STATICV6", "STATICV4_DHCPV6", "STATICV4_AUTOV6", "DHCPV4_STATICV6", "DHCPV4_DHCPV6", "DHCPV4_AUTOV6", "Static", "Dynamic", ] 
**deploymentOption** | str,  | str,  | number of NICs. It can be onenic,twonic,threenic,onenic-large,twonic-large,threenic-large | [optional] 
**DNS** | str,  | str,  | DNS server addresses | [optional] 
**DNS0** | str,  | str,  | Internet DNS | [optional] 
**forwardrules** | str,  | str,  | Comma separated list of forward rules in the form {tcp|udp}/listening-port-number/destination-ip-address:destination-port-number | [optional] 
**v6ip0** | str,  | str,  | NIC 1 (eth0) IPv6 address | [optional] 
**v6ip1** | str,  | str,  | NIC 2 (eth1) IPv6 address | [optional] 
**v6ip2** | str,  | str,  | NIC 3 (eth2) IPv6 address | [optional] 
**ipv6prefix0** | str,  | str,  | NIC 1 (eth0) Host Network Prefix | [optional] 
**ipv6prefix1** | str,  | str,  | NIC 2 (eth1) Host Network Prefix | [optional] 
**ipv6prefix2** | str,  | str,  | NIC 3 (eth2) Host Network Prefix | [optional] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

