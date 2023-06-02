# swagger_client.VirtualMachineInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_cluster_system_virtual_machines_get**](VirtualMachineInformationApi.md#v1_cluster_system_virtual_machines_get) | **GET** /v1/cluster/system-virtual-machines | Get information about system virtual machines

# **v1_cluster_system_virtual_machines_get**
> list[SystemVMInfo] v1_cluster_system_virtual_machines_get()

Get information about system virtual machines

Get the name, status, and host information for system virtual machines in the VxRail cluster (Witness VM which is deployed in the witness sled in VxRail VD-4000r or VD-4000z platforms is not included).

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
api_instance = swagger_client.VirtualMachineInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get information about system virtual machines
    api_response = api_instance.v1_cluster_system_virtual_machines_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VirtualMachineInformationApi->v1_cluster_system_virtual_machines_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[SystemVMInfo]**](SystemVMInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

