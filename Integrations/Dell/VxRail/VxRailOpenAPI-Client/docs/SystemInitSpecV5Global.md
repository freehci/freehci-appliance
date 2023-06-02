# SystemInitSpecV5Global

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ip_version** | **str** | IPv4 is the default value. IPv6 and DUALSTACK are for internal use only. | [optional] 
**ntp_servers** | **list[str]** | Array of IP addresses for the NTP servers | [optional] 
**is_internal_dns** | **bool** | Whether the DNS server is internal | [optional] 
**dns_servers** | **list[str]** | Array of IP addresses for the DNS servers | [optional] 
**syslog_servers** | **list[str]** | Array of IP addresses for the Syslog servers | [optional] 
**cluster_type** | **str** | Type of cluster | [optional] 
**cluster_vsan_prefix_length_ipv6** | **int** | Internal use only | [optional] 
**cluster_vmotion_prefix_length_ipv6** | **int** | Internal use only | [optional] 
**cluster_management_prefix_length_ipv6** | **int** | Internal use only | [optional] 
**cluster_management_gateway_ipv6** | **str** | Internal use only | [optional] 
**cluster_systemvm_netmask** | **str** | Subnet mask for cluster management nodes | [optional] 
**cluster_systemvm_gateway** | **str** | Gateway address for cluster management nodes | [optional] 
**cluster_systemvm_prefix_length_ipv6** | **int** | Internal use only | [optional] 
**cluster_systemvm_gateway_ipv6** | **str** | Internal use only | [optional] 
**cluster_management_netmask** | **str** | Subnet mask for cluster management nodes | [optional] 
**cluster_management_gateway** | **str** | Gateway address for cluster management nodes | [optional] 
**cluster_vsan_netmask** | **str** | Subnet mask for the vSAN cluster | [optional] 
**cluster_vmotion_netmask** | **str** | Subnet mask for the vSphere vMotion cluster | [optional] 
**cluster_witness_netmask** | **str** | Subnet mask for the witness nodes | [optional] 
**cluster_witness_gateway** | **str** | Gateway address for the witness nodes | [optional] 
**top_level_domain** | **str** | Top-level domain name | [optional] 
**ha_isolation_addresses** | **list[str]** | An array of the IP addresses for the vSphere HA isolation | [optional] 
**is_vlcm_cluster** | **bool** | Enable vlcm | [optional] 
**is_vlcm_force_remediate** | **bool** | Remediate the cluster after vLCM enablement. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

