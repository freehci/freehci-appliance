# swagger_client.DiskInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_disks_get**](DiskInformationApi.md#v1_disks_get) | **GET** /v1/disks | Get a list of disks
[**v1_disks_sn_get**](DiskInformationApi.md#v1_disks_sn_get) | **GET** /v1/disks/{disk_sn} | Get information about a disk

# **v1_disks_get**
> list[DiskInfo] v1_disks_get()

Get a list of disks

Retrieve a list of disk drives and their associated information.

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
api_instance = swagger_client.DiskInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of disks
    api_response = api_instance.v1_disks_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DiskInformationApi->v1_disks_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[DiskInfo]**](DiskInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_disks_sn_get**
> DiskInfo v1_disks_sn_get(disk_sn)

Get information about a disk

Retrieve information about a specific disk drive.

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
api_instance = swagger_client.DiskInformationApi(swagger_client.ApiClient(configuration))
disk_sn = 'disk_sn_example' # str | The serial number of disk that you want to query.

try:
    # Get information about a disk
    api_response = api_instance.v1_disks_sn_get(disk_sn)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DiskInformationApi->v1_disks_sn_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **disk_sn** | **str**| The serial number of disk that you want to query. | 

### Return type

[**DiskInfo**](DiskInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

