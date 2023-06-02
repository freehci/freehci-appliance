# swagger_client.DiskSlotMappingApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_hosts_disk_slot_mappings_get**](DiskSlotMappingApi.md#v1_hosts_disk_slot_mappings_get) | **GET** /v1/hosts/disk-slot-mappings | Get disk slot mappings for hosts

# **v1_hosts_disk_slot_mappings_get**
> list[HostDiskSlotMappingsResponse] v1_hosts_disk_slot_mappings_get(body)

Get disk slot mappings for hosts

Get disk slot mappings for hosts.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: basicAuth
configuration = swagger_client.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = swagger_client.DiskSlotMappingApi(swagger_client.ApiClient(configuration))
body = swagger_client.HostsDiskslotmappingsBody() # HostsDiskslotmappingsBody | Information needed to retrieve slot mappings for a host.

try:
    # Get disk slot mappings for hosts
    api_response = api_instance.v1_hosts_disk_slot_mappings_get(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DiskSlotMappingApi->v1_hosts_disk_slot_mappings_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HostsDiskslotmappingsBody**](HostsDiskslotmappingsBody.md)| Information needed to retrieve slot mappings for a host. | 

### Return type

[**list[HostDiskSlotMappingsResponse]**](HostDiskSlotMappingsResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

