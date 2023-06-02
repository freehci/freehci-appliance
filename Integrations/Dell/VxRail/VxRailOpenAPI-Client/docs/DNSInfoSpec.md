# DNSInfoSpec

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**components** | **str** | Indicates which DNS servers are updated. Supported values are \&quot;VXM\&quot; or \&quot;ALL\&quot;. \&quot;ALL\&quot; is the default. If ALL is set, all DNS servers in the cluster are replaced. If VXM is set, only the DNS server for VxRail Manager is replaced. | 
**vcenter** | [**User**](User.md) |  | 
**servers** | **list[str]** | A list of IP addresses for the DNS servers | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

