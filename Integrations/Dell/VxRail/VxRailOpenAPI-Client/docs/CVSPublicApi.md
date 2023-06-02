# swagger_client.CVSPublicApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**generate_advisory_report_public**](CVSPublicApi.md#generate_advisory_report_public) | **POST** /v1/lcm/advisory-report | Generate an advisory report of all online and local updates
[**generate_compliance_report_public**](CVSPublicApi.md#generate_compliance_report_public) | **POST** /v1/cvs/compliance-report | Generate a compliance drift report
[**lcm_advisory_meta_bundle_post**](CVSPublicApi.md#lcm_advisory_meta_bundle_post) | **POST** /v1/lcm/advisory-meta-bundle | Upload an advisory metadata bundle

# **generate_advisory_report_public**
> GenerateReportSuccessResponse generate_advisory_report_public()

Generate an advisory report of all online and local updates

Generate an advisory report that contains information about all online and local lifecycle management updates.

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
api_instance = swagger_client.CVSPublicApi(swagger_client.ApiClient(configuration))

try:
    # Generate an advisory report of all online and local updates
    api_response = api_instance.generate_advisory_report_public()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CVSPublicApi->generate_advisory_report_public: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**GenerateReportSuccessResponse**](GenerateReportSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generate_compliance_report_public**
> GenerateReportSuccessResponse generate_compliance_report_public()

Generate a compliance drift report

Generate a compliance report containing component drift information against the current system baseline.

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
api_instance = swagger_client.CVSPublicApi(swagger_client.ApiClient(configuration))

try:
    # Generate a compliance drift report
    api_response = api_instance.generate_compliance_report_public()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CVSPublicApi->generate_compliance_report_public: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**GenerateReportSuccessResponse**](GenerateReportSuccessResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **lcm_advisory_meta_bundle_post**
> lcm_advisory_meta_bundle_post(meta_bundle=meta_bundle)

Upload an advisory metadata bundle

Upload a metadata bundle for local advisory analysis.

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
api_instance = swagger_client.CVSPublicApi(swagger_client.ApiClient(configuration))
meta_bundle = 'meta_bundle_example' # str |  (optional)

try:
    # Upload an advisory metadata bundle
    api_instance.lcm_advisory_meta_bundle_post(meta_bundle=meta_bundle)
except ApiException as e:
    print("Exception when calling CVSPublicApi->lcm_advisory_meta_bundle_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **meta_bundle** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

