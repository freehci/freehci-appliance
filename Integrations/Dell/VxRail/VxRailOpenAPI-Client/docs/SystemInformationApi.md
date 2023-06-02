# swagger_client.SystemInformationApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**query_vx_rail_manager_system_information**](SystemInformationApi.md#query_vx_rail_manager_system_information) | **GET** /v1/system | Get VxRail system information (v1)
[**query_vx_rail_manager_system_information_v2**](SystemInformationApi.md#query_vx_rail_manager_system_information_v2) | **GET** /v2/system | Get VxRail system information (v2)
[**query_vx_rail_manager_system_information_v3**](SystemInformationApi.md#query_vx_rail_manager_system_information_v3) | **GET** /v3/system | Get VxRail system information (v3)
[**query_vx_rail_manager_system_information_v4**](SystemInformationApi.md#query_vx_rail_manager_system_information_v4) | **GET** /v4/system | Get VxRail system information (v4)
[**query_vx_rail_manager_system_information_v5**](SystemInformationApi.md#query_vx_rail_manager_system_information_v5) | **GET** /v5/system | Get VxRail system information (v5).
[**v1_system_available_hosts_get**](SystemInformationApi.md#v1_system_available_hosts_get) | **GET** /v1/system/available-hosts | Get information about available hosts
[**v1_system_cluster_hosts_get**](SystemInformationApi.md#v1_system_cluster_hosts_get) | **GET** /v1/system/cluster-hosts | Get information about configured hosts
[**v1_system_dns_get**](SystemInformationApi.md#v1_system_dns_get) | **GET** /v1/system/dns | Get DNS of VxRail cluster
[**v1_system_dns_post**](SystemInformationApi.md#v1_system_dns_post) | **POST** /v1/system/dns | Set DNS of VxRail cluster
[**v1_system_ntp_get**](SystemInformationApi.md#v1_system_ntp_get) | **GET** /v1/system/ntp | Get NTP of VxRail cluster
[**v1_system_ntp_post**](SystemInformationApi.md#v1_system_ntp_post) | **POST** /v1/system/ntp | Set NTP of VxRail cluster
[**v1_system_primary_storage_post**](SystemInformationApi.md#v1_system_primary_storage_post) | **POST** /v1/system/primary-storage | Provision and finalize a dynamic node cluster
[**v2_system_cluster_hosts_get**](SystemInformationApi.md#v2_system_cluster_hosts_get) | **GET** /v2/system/cluster-hosts | Get information about configured hosts

# **query_vx_rail_manager_system_information**
> VxmSystemInfo query_vx_rail_manager_system_information()

Get VxRail system information (v1)

Get VxRail system information (v1).

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail system information (v1)
    api_response = api_instance.query_vx_rail_manager_system_information()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->query_vx_rail_manager_system_information: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**VxmSystemInfo**](VxmSystemInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_vx_rail_manager_system_information_v2**
> VxmSystemInfoV2 query_vx_rail_manager_system_information_v2()

Get VxRail system information (v2)

Get VxRail system information (v2).

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail system information (v2)
    api_response = api_instance.query_vx_rail_manager_system_information_v2()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->query_vx_rail_manager_system_information_v2: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**VxmSystemInfoV2**](VxmSystemInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_vx_rail_manager_system_information_v3**
> VxmSystemInfoV3 query_vx_rail_manager_system_information_v3()

Get VxRail system information (v3)

Get VxRail system information (v3).

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail system information (v3)
    api_response = api_instance.query_vx_rail_manager_system_information_v3()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->query_vx_rail_manager_system_information_v3: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**VxmSystemInfoV3**](VxmSystemInfoV3.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_vx_rail_manager_system_information_v4**
> VxmSystemInfoV4 query_vx_rail_manager_system_information_v4()

Get VxRail system information (v4)

Get VxRail system information (v4). Added support for satellite nodes.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail system information (v4)
    api_response = api_instance.query_vx_rail_manager_system_information_v4()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->query_vx_rail_manager_system_information_v4: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**VxmSystemInfoV4**](VxmSystemInfoV4.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_vx_rail_manager_system_information_v5**
> InlineResponse2001 query_vx_rail_manager_system_information_v5()

Get VxRail system information (v5).

VxRail system information (v5). If the cluster type is dynamic node, then Deployment_type displays \"DYNAMIC_NODE\" instead of \"COMPUTE\".

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get VxRail system information (v5).
    api_response = api_instance.query_vx_rail_manager_system_information_v5()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->query_vx_rail_manager_system_information_v5: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_available_hosts_get**
> list[DiscoveredNodeInfo] v1_system_available_hosts_get(filter=filter)

Get information about available hosts

Get information about available hosts in the VxRail cluster.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))
filter = 'filter_example' # str | The user can filter a list of hosts by the fields (id, appliance_id, slot, model, is_primary_node, bios_uuid, cluster_affinity) using the supported operators (eq and ne). (optional)

try:
    # Get information about available hosts
    api_response = api_instance.v1_system_available_hosts_get(filter=filter)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v1_system_available_hosts_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| The user can filter a list of hosts by the fields (id, appliance_id, slot, model, is_primary_node, bios_uuid, cluster_affinity) using the supported operators (eq and ne). | [optional] 

### Return type

[**list[DiscoveredNodeInfo]**](DiscoveredNodeInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_cluster_hosts_get**
> list[ClusterHostInfo] v1_system_cluster_hosts_get(filter=filter)

Get information about configured hosts

Get information about configured hosts in the VxRail cluster.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))
filter = 'filter_example' # str | The user can filter a list of hosts by the fields (id, appliance_id, slot, model, is_primary_node, bios_uuid, cluster_affinity) using the supported operators (eq and ne). (optional)

try:
    # Get information about configured hosts
    api_response = api_instance.v1_system_cluster_hosts_get(filter=filter)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v1_system_cluster_hosts_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| The user can filter a list of hosts by the fields (id, appliance_id, slot, model, is_primary_node, bios_uuid, cluster_affinity) using the supported operators (eq and ne). | [optional] 

### Return type

[**list[ClusterHostInfo]**](ClusterHostInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_dns_get**
> DNSInfo v1_system_dns_get()

Get DNS of VxRail cluster

Get information about the DNS servers for the cluster (Witness VM which is deployed in the witness sled in VxRail VD-4000r or VD-4000z platforms is not included).

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get DNS of VxRail cluster
    api_response = api_instance.v1_system_dns_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v1_system_dns_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**DNSInfo**](DNSInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_dns_post**
> DNSInfo v1_system_dns_post(body)

Set DNS of VxRail cluster

Set the DNS servers for the cluster.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))
body = swagger_client.DNSInfoSpec() # DNSInfoSpec | DNS servers for VxRail cluster

try:
    # Set DNS of VxRail cluster
    api_response = api_instance.v1_system_dns_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v1_system_dns_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DNSInfoSpec**](DNSInfoSpec.md)| DNS servers for VxRail cluster | 

### Return type

[**DNSInfo**](DNSInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_ntp_get**
> NTPInfo v1_system_ntp_get()

Get NTP of VxRail cluster

Get information about the NTP servers for the cluster.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))

try:
    # Get NTP of VxRail cluster
    api_response = api_instance.v1_system_ntp_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v1_system_ntp_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**NTPInfo**](NTPInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_ntp_post**
> NTPInfo v1_system_ntp_post(body)

Set NTP of VxRail cluster

Set the NTP servers for the cluster.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))
body = swagger_client.NTPInfoSpec() # NTPInfoSpec | Information to set the NTP servers for the cluster.

try:
    # Set NTP of VxRail cluster
    api_response = api_instance.v1_system_ntp_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v1_system_ntp_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**NTPInfoSpec**](NTPInfoSpec.md)| Information to set the NTP servers for the cluster. | 

### Return type

[**NTPInfo**](NTPInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_system_primary_storage_post**
> v1_system_primary_storage_post(body)

Provision and finalize a dynamic node cluster

Provision and finalize a dynamic node cluster, such as moving the VxRail Manager virtual machine to the target shared storage, enabling high availability (HA) and distributed resource scheduler (DRS) service on the cluster, and enabling post-installation functions.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))
body = swagger_client.PrimaryStorageSpec() # PrimaryStorageSpec | Information to provision a dynamic node cluster

try:
    # Provision and finalize a dynamic node cluster
    api_instance.v1_system_primary_storage_post(body)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v1_system_primary_storage_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PrimaryStorageSpec**](PrimaryStorageSpec.md)| Information to provision a dynamic node cluster | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_system_cluster_hosts_get**
> list[ClusterHostInfoV2] v2_system_cluster_hosts_get(filter=filter)

Get information about configured hosts

Get information about configured hosts in the VxRail cluster.

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
api_instance = swagger_client.SystemInformationApi(swagger_client.ApiClient(configuration))
filter = 'filter_example' # str | The user can filter a list of hosts by the fields (id, appliance_id, slot, model, is_primary_node, bios_uuid, cluster_affinity) using the supported operators (eq and ne). (optional)

try:
    # Get information about configured hosts
    api_response = api_instance.v2_system_cluster_hosts_get(filter=filter)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemInformationApi->v2_system_cluster_hosts_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| The user can filter a list of hosts by the fields (id, appliance_id, slot, model, is_primary_node, bios_uuid, cluster_affinity) using the supported operators (eq and ne). | [optional] 

### Return type

[**list[ClusterHostInfoV2]**](ClusterHostInfoV2.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

