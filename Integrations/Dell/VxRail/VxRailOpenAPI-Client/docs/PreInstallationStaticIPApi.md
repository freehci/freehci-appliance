# swagger_client.PreInstallationStaticIPApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_network_vxm_post**](PreInstallationStaticIPApi.md#v1_network_vxm_post) | **POST** /v1/network/vxrail-manager | Configure the Management IP address for VxRail Manager
[**v2_network_vxm_post**](PreInstallationStaticIPApi.md#v2_network_vxm_post) | **POST** /v2/network/vxrail-manager | Configure the Management IP address for VxRail Manager

# **v1_network_vxm_post**
> NetworkVxMInfo v1_network_vxm_post(body)

Configure the Management IP address for VxRail Manager

Configure VxRail Manager with a static IP address for remote access. This endpoint uses the default static IP address (192.168.10.200) and can only be run before the initial configuration and deployment of a VxRail cluster.

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
api_instance = swagger_client.PreInstallationStaticIPApi(swagger_client.ApiClient(configuration))
body = swagger_client.StaticIPSettingsSpec() # StaticIPSettingsSpec | The parameters that are required for setting the VxRail Manager static IP address.

try:
    # Configure the Management IP address for VxRail Manager
    api_response = api_instance.v1_network_vxm_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PreInstallationStaticIPApi->v1_network_vxm_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StaticIPSettingsSpec**](StaticIPSettingsSpec.md)| The parameters that are required for setting the VxRail Manager static IP address. | 

### Return type

[**NetworkVxMInfo**](NetworkVxMInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_network_vxm_post**
> NetworkVxMInfo v2_network_vxm_post(body)

Configure the Management IP address for VxRail Manager

Configure VxRail Manager with a static IP address for remote access. This endpoint uses the default static IP address (192.168.10.200) and can only be run before the initial configuration and deployment of a VxRail cluster.

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
api_instance = swagger_client.PreInstallationStaticIPApi(swagger_client.ApiClient(configuration))
body = swagger_client.StaticIPSettingsSpecV2() # StaticIPSettingsSpecV2 | The parameters that are required for setting the VxRail Manager static IP address.

try:
    # Configure the Management IP address for VxRail Manager
    api_response = api_instance.v2_network_vxm_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PreInstallationStaticIPApi->v2_network_vxm_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StaticIPSettingsSpecV2**](StaticIPSettingsSpecV2.md)| The parameters that are required for setting the VxRail Manager static IP address. | 

### Return type

[**NetworkVxMInfo**](NetworkVxMInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

