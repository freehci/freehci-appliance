# openapi_client.model.load_balancer_settings.LoadBalancerSettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**virtualIPAddress** | str,  | str,  | Virtual IP address used by Load Balancer | 
**groupID** | decimal.Decimal, int,  | decimal.Decimal,  | Load balancer Group ID. Give value between 1 - 255 | value must be a 32 bit integer
**loadBalancerMode** | str,  | str,  | Mode for Load Balancer. ONEARM - UAG in a cluster load balancing each otherINLINE - UAG acting as load balancer load balancing other UAG&#x27;s behind it | must be one of ["DISABLED", "ONEARM", ] 
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

