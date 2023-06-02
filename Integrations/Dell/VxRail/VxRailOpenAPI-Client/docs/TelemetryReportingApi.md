# swagger_client.TelemetryReportingApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_post_telemetry_tier_setting_information**](TelemetryReportingApi.md#v1_post_telemetry_tier_setting_information) | **POST** /v1/telemetry/tier | Set the telemetry tier
[**v1_query_telemetry_tier_setting_information**](TelemetryReportingApi.md#v1_query_telemetry_tier_setting_information) | **GET** /v1/telemetry/tier | Get the telemetry tier

# **v1_post_telemetry_tier_setting_information**
> v1_post_telemetry_tier_setting_information(body)

Set the telemetry tier

Set the telemetry tier.

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
api_instance = swagger_client.TelemetryReportingApi(swagger_client.ApiClient(configuration))
body = swagger_client.TelemetryTierSetting() # TelemetryTierSetting | Level of telemetry tier to be set

try:
    # Set the telemetry tier
    api_instance.v1_post_telemetry_tier_setting_information(body)
except ApiException as e:
    print("Exception when calling TelemetryReportingApi->v1_post_telemetry_tier_setting_information: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**TelemetryTierSetting**](TelemetryTierSetting.md)| Level of telemetry tier to be set | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_query_telemetry_tier_setting_information**
> TelemetryTierSetting v1_query_telemetry_tier_setting_information()

Get the telemetry tier

Retrieve the currently set telemetry tier.

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
api_instance = swagger_client.TelemetryReportingApi(swagger_client.ApiClient(configuration))

try:
    # Get the telemetry tier
    api_response = api_instance.v1_query_telemetry_tier_setting_information()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryReportingApi->v1_query_telemetry_tier_setting_information: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**TelemetryTierSetting**](TelemetryTierSetting.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

