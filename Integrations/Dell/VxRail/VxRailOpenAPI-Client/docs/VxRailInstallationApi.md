# swagger_client.VxRailInstallationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_system_initialize_customer_supplied_hosts_post**](VxRailInstallationApi.md#v1_system_initialize_customer_supplied_hosts_post) | **POST** /v1/system/initialize/customer-supplied-hosts | Return nodes by customer supplied management IP
[**v1_system_initialize_disk_slot_mappings_get**](VxRailInstallationApi.md#v1_system_initialize_disk_slot_mappings_get) | **GET** /v1/system/initialize/disk-slot-mappings | Get disk slot mappings for hosts
[**v1_system_initialize_nodes_get**](VxRailInstallationApi.md#v1_system_initialize_nodes_get) | **GET** /v1/system/initialize/nodes | Return nodes by auto discovery
[**v1_system_initialize_post**](VxRailInstallationApi.md#v1_system_initialize_post) | **POST** /v1/system/initialize | Configure and deploy a new VxRail cluster
[**v1_system_initialize_status_get**](VxRailInstallationApi.md#v1_system_initialize_status_get) | **GET** /v1/system/initialize/status | Get VxRail cluster configuration and deployment status
[**v2_system_initialize_customer_supplied_hosts_post**](VxRailInstallationApi.md#v2_system_initialize_customer_supplied_hosts_post) | **POST** /v2/system/initialize/customer-supplied-hosts | Return nodes by customer supplied management IP
[**v2_system_initialize_nodes_get**](VxRailInstallationApi.md#v2_system_initialize_nodes_get) | **GET** /v2/system/initialize/nodes | Return nodes by auto discovery

# **v1_system_initialize_customer_supplied_hosts_post**
> list[DiscoveredNodeInfoV2] v1_system_initialize_customer_supplied_hosts_post(body)

Return nodes by customer supplied management IP

Return nodes by the customer supplied node management IP address and ESXi root password.

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
api_instance = swagger_client.VxRailInstallationApi(swagger_client.ApiClient(configuration))
body = [swagger_client.CustomerSuppliedHostInfo()] # list[CustomerSuppliedHostInfo] | Management IP and password for all customer supplied hosts

try:
    # Return nodes by customer supplied management IP
    api_response = api_instance.v1_system_initialize_customer_supplied_hosts_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VxRailInstallationApi->v1_system_initialize_customer_supplied_hosts_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[CustomerSuppliedHostInfo]**](CustomerSuppliedHostInfo.md)| Management IP and password for all customer supplied hosts | 

### Return type

[**list[DiscoveredNodeInfoV2]**](DiscoveredNodeInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_initialize_disk_slot_mappings_get**
> list[HostDiskSlotMappingsResponse] v1_system_initialize_disk_slot_mappings_get(body)

Get disk slot mappings for hosts

Retrieve disk slots and usage mappings from the initial configuration for a set of hosts.

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
api_instance = swagger_client.VxRailInstallationApi(swagger_client.ApiClient(configuration))
body = swagger_client.InitializeDiskslotmappingsBody() # InitializeDiskslotmappingsBody | Information needed to retrieve disk slot usage for a host

try:
    # Get disk slot mappings for hosts
    api_response = api_instance.v1_system_initialize_disk_slot_mappings_get(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VxRailInstallationApi->v1_system_initialize_disk_slot_mappings_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**InitializeDiskslotmappingsBody**](InitializeDiskslotmappingsBody.md)| Information needed to retrieve disk slot usage for a host | 

### Return type

[**list[HostDiskSlotMappingsResponse]**](HostDiskSlotMappingsResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_initialize_nodes_get**
> list[DiscoveredNodeInfoV2] v1_system_initialize_nodes_get()

Return nodes by auto discovery

Return nodes discovered by auto discovery.

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
api_instance = swagger_client.VxRailInstallationApi(swagger_client.ApiClient(configuration))

try:
    # Return nodes by auto discovery
    api_response = api_instance.v1_system_initialize_nodes_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VxRailInstallationApi->v1_system_initialize_nodes_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[DiscoveredNodeInfoV2]**](DiscoveredNodeInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_initialize_post**
> InlineResponse202 v1_system_initialize_post(body, dryrun=dryrun)

Configure and deploy a new VxRail cluster

Configure and deploy a new VxRail cluster.

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
api_instance = swagger_client.VxRailInstallationApi(swagger_client.ApiClient(configuration))
body = swagger_client.SystemInitSpecV5() # SystemInitSpecV5 | JSON configuration parameters to initialize the VxRail system
dryrun = true # bool | Performs a validation of the initial input configuration. Set true to cause a dry run and false to configure and deploy a new cluster. The default value is false. (optional)

try:
    # Configure and deploy a new VxRail cluster
    api_response = api_instance.v1_system_initialize_post(body, dryrun=dryrun)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VxRailInstallationApi->v1_system_initialize_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SystemInitSpecV5**](SystemInitSpecV5.md)| JSON configuration parameters to initialize the VxRail system | 
 **dryrun** | **bool**| Performs a validation of the initial input configuration. Set true to cause a dry run and false to configure and deploy a new cluster. The default value is false. | [optional] 

### Return type

[**InlineResponse202**](InlineResponse202.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_initialize_status_get**
> Day1RequestInfo v1_system_initialize_status_get()

Get VxRail cluster configuration and deployment status

Retrieve VxRail cluster configuration and deployment status information.

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
api_instance = swagger_client.VxRailInstallationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail cluster configuration and deployment status
    api_response = api_instance.v1_system_initialize_status_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VxRailInstallationApi->v1_system_initialize_status_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Day1RequestInfo**](Day1RequestInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_system_initialize_customer_supplied_hosts_post**
> DiscoveredNodesInfoV4 v2_system_initialize_customer_supplied_hosts_post(body)

Return nodes by customer supplied management IP

Return nodes by the customer supplied node management IP address and ESXi root password.

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
api_instance = swagger_client.VxRailInstallationApi(swagger_client.ApiClient(configuration))
body = [swagger_client.CustomerSuppliedHostInfo()] # list[CustomerSuppliedHostInfo] | Management IP and password for all customer supplied hosts

try:
    # Return nodes by customer supplied management IP
    api_response = api_instance.v2_system_initialize_customer_supplied_hosts_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VxRailInstallationApi->v2_system_initialize_customer_supplied_hosts_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[CustomerSuppliedHostInfo]**](CustomerSuppliedHostInfo.md)| Management IP and password for all customer supplied hosts | 

### Return type

[**DiscoveredNodesInfoV4**](DiscoveredNodesInfoV4.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_system_initialize_nodes_get**
> DiscoveredNodesInfoV4 v2_system_initialize_nodes_get()

Return nodes by auto discovery

Return nodes discovered by auto discovery.

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
api_instance = swagger_client.VxRailInstallationApi(swagger_client.ApiClient(configuration))

try:
    # Return nodes by auto discovery
    api_response = api_instance.v2_system_initialize_nodes_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VxRailInstallationApi->v2_system_initialize_nodes_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**DiscoveredNodesInfoV4**](DiscoveredNodesInfoV4.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

