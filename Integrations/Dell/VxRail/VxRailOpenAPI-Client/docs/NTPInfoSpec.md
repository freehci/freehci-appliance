# NTPInfoSpec

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**components** | **str** | Indicates which NTP servers are updated. Supported values are \&quot;VXM\&quot; or \&quot;ALL\&quot;. \&quot;ALL\&quot; is the default. If ALL is set, all NTP servers in the cluster are replaced. If VXM is set, only the NTP server for VxRail Manager is replaced. | 
**vcenter** | [**User**](User.md) |  | 
**servers** | **list[str]** | A list of IP addresses for the NTP servers | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

