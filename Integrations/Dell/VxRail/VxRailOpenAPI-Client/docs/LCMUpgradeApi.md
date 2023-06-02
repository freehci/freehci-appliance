# swagger_client.LCMUpgradeApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**upgrade_retry_v1**](LCMUpgradeApi.md#upgrade_retry_v1) | **POST** /v1/lcm/upgrade/retry | Perform a retry upgrade of the VxRail system (v1)
[**upgrade_v1**](LCMUpgradeApi.md#upgrade_v1) | **POST** /v1/lcm/upgrade | Perform a full upgrade of the VxRail system (v1)
[**upgrade_v2**](LCMUpgradeApi.md#upgrade_v2) | **POST** /v2/lcm/upgrade | Perform a full upgrade of the VxRail system (v2)
[**upgrade_v3**](LCMUpgradeApi.md#upgrade_v3) | **POST** /v3/lcm/upgrade | Perform a full upgrade of the VxRail system (v3)
[**upgrade_v4**](LCMUpgradeApi.md#upgrade_v4) | **POST** /v4/lcm/upgrade | Perform a partial upgrade of the VxRail system (v4)
[**upgrade_v5**](LCMUpgradeApi.md#upgrade_v5) | **POST** /v5/lcm/upgrade | Perform an upgrade for the VxRail software and hardware with the options to either skip the failed node and ignore the missing file check (v5).
[**upgrade_v6**](LCMUpgradeApi.md#upgrade_v6) | **POST** /v6/lcm/upgrade | Perform an upgrade for the VxRail software and hardware and allow customer updates management account during LCM(v6).
[**vlcm_image_query**](LCMUpgradeApi.md#vlcm_image_query) | **POST** /v1/lcm/upgrade/vlcm/image | 

# **upgrade_retry_v1**
> AsyncLcmRequestSuccessResponse upgrade_retry_v1()

Perform a retry upgrade of the VxRail system (v1)

Perform a retry upgrade for all VxRail software and hardware after previous upgrade failed.

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))

try:
    # Perform a retry upgrade of the VxRail system (v1)
    api_response = api_instance.upgrade_retry_v1()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->upgrade_retry_v1: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upgrade_v1**
> AsyncLcmRequestSuccessResponse upgrade_v1(body)

Perform a full upgrade of the VxRail system (v1)

Perform a full upgrade for all VxRail software and hardware. Supported in VxRail versions 4.5.3xx+, 4.7.x, 7.0.x. [NOTE] When upgrading from VxRail 4.7.515 or earlier to VxRail 7.0.200 or later, you must upload the upgrade bundle to a folder that is not part of the root file system.

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))
body = swagger_client.UpgradeSpecV1() # UpgradeSpecV1 | Input parameters needed for the upgrade

try:
    # Perform a full upgrade of the VxRail system (v1)
    api_response = api_instance.upgrade_v1(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->upgrade_v1: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpgradeSpecV1**](UpgradeSpecV1.md)| Input parameters needed for the upgrade | 

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upgrade_v2**
> AsyncLcmRequestSuccessResponse upgrade_v2(body)

Perform a full upgrade of the VxRail system (v2)

Perform a full upgrade for all VxRail software and hardware. Supported in VxRail versions 4.7.410+, 7.0.x. [NOTE] When upgrading from VxRail 4.7.515 or earlier to VxRail 7.0.200 or later, you must upload the upgrade bundle to a folder that is not part of the root file system.

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))
body = swagger_client.UpgradeSpecV2() # UpgradeSpecV2 | Input parameters needed for the upgrade

try:
    # Perform a full upgrade of the VxRail system (v2)
    api_response = api_instance.upgrade_v2(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->upgrade_v2: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpgradeSpecV2**](UpgradeSpecV2.md)| Input parameters needed for the upgrade | 

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upgrade_v3**
> AsyncLcmRequestSuccessResponse upgrade_v3(body)

Perform a full upgrade of the VxRail system (v3)

Perform a full upgrade for all VxRail software and hardware. Supported in VxRail versions 7.0.100+.

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))
body = swagger_client.UpgradeSpecV3() # UpgradeSpecV3 | Input parameters needed for the upgrade

try:
    # Perform a full upgrade of the VxRail system (v3)
    api_response = api_instance.upgrade_v3(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->upgrade_v3: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpgradeSpecV3**](UpgradeSpecV3.md)| Input parameters needed for the upgrade | 

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upgrade_v4**
> AsyncLcmRequestSuccessResponse upgrade_v4(body)

Perform a partial upgrade of the VxRail system (v4)

Perform a partial upgrade for VxRail software and hardware (supported in VxRail versions 7.0.240 and later). Version 4 of this API includes an optional property called \"target_hosts\", which indicates the nodes that should be upgraded. If the property is empty, then this API upgrades all nodes in the cluster.

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))
body = swagger_client.UpgradeSpecV4() # UpgradeSpecV4 | Input parameters needed for the upgrade

try:
    # Perform a partial upgrade of the VxRail system (v4)
    api_response = api_instance.upgrade_v4(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->upgrade_v4: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpgradeSpecV4**](UpgradeSpecV4.md)| Input parameters needed for the upgrade | 

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upgrade_v5**
> AsyncLcmRequestSuccessResponse upgrade_v5(body)

Perform an upgrade for the VxRail software and hardware with the options to either skip the failed node and ignore the missing file check (v5).

Perform an upgrade for the VxRail software and hardware with the options to skip the failed node, ignore the missing file check, and pre-check the rule for ecosystem components (v5).

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))
body = swagger_client.UpgradeSpecV5() # UpgradeSpecV5 | Input parameters needed for the upgrade

try:
    # Perform an upgrade for the VxRail software and hardware with the options to either skip the failed node and ignore the missing file check (v5).
    api_response = api_instance.upgrade_v5(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->upgrade_v5: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpgradeSpecV5**](UpgradeSpecV5.md)| Input parameters needed for the upgrade | 

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upgrade_v6**
> AsyncLcmRequestSuccessResponse upgrade_v6(body)

Perform an upgrade for the VxRail software and hardware and allow customer updates management account during LCM(v6).

Perform an upgrade for the VxRail software and hardware. Version 6 of this API includes the following option -- \"vc_mgmt_user\", the new management account. The system will create the account @vsphere.local domain and assign management roles or privileges to it during LCM(v6).

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))
body = swagger_client.UpgradeSpecV6() # UpgradeSpecV6 | Input parameters needed for the upgrade

try:
    # Perform an upgrade for the VxRail software and hardware and allow customer updates management account during LCM(v6).
    api_response = api_instance.upgrade_v6(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->upgrade_v6: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UpgradeSpecV6**](UpgradeSpecV6.md)| Input parameters needed for the upgrade | 

### Return type

[**AsyncLcmRequestSuccessResponse**](AsyncLcmRequestSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **vlcm_image_query**
> VlcmImageDepotInfo vlcm_image_query(body)



Request to fetch the vLCM image information in the LCM bundle that is provided.

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
api_instance = swagger_client.LCMUpgradeApi(swagger_client.ApiClient(configuration))
body = swagger_client.VlcmUpgradeImageDepotSpec() # VlcmUpgradeImageDepotSpec | Input parameters that are required to query the vLCM image content.

try:
    api_response = api_instance.vlcm_image_query(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling LCMUpgradeApi->vlcm_image_query: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VlcmUpgradeImageDepotSpec**](VlcmUpgradeImageDepotSpec.md)| Input parameters that are required to query the vLCM image content. | 

### Return type

[**VlcmImageDepotInfo**](VlcmImageDepotInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

