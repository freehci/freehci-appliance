# swagger_client.CertificatesApi

All URIs are relative to *https://raw.githubusercontent.com/rest/vxm*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_certificates_csr_post**](CertificatesApi.md#v1_certificates_csr_post) | **POST** /v1/certificates/csr | Generate a Certificate Signing Request.
[**v1_certificates_import_vxm_post**](CertificatesApi.md#v1_certificates_import_vxm_post) | **POST** /v1/certificates/import-vxm | Update the VxRail Manager certificate(Version 1)
[**v1_certificates_scep_config_get**](CertificatesApi.md#v1_certificates_scep_config_get) | **GET** /v1/cluster/certificates/scep/config | Get automated renewal configurations of the certificate
[**v1_certificates_scep_config_post**](CertificatesApi.md#v1_certificates_scep_config_post) | **POST** /v1/cluster/certificates/scep/config | Update automated renewal configurations of certificate through SCEP
[**v1_certificates_scep_status_get**](CertificatesApi.md#v1_certificates_scep_status_get) | **GET** /v1/cluster/certificates/scep/status | Get automated renewal status of the certificate
[**v1_certificates_validate_post**](CertificatesApi.md#v1_certificates_validate_post) | **POST** /v1/certificates/validate | Verify the certificate
[**v1_trust_store_certificates_fingerprint_delete**](CertificatesApi.md#v1_trust_store_certificates_fingerprint_delete) | **DELETE** /v1/trust-store/certificates/{fingerprint} | Delete the certificate file from the VxRail Manager trust store according to the fingerprint.
[**v1_trust_store_certificates_fingerprint_get**](CertificatesApi.md#v1_trust_store_certificates_fingerprint_get) | **GET** /v1/trust-store/certificates/{fingerprint} | Search the VxRail Manager trust store and get the certificate content information (PEM form) according to fingerprint parameter.
[**v1_trust_store_certificates_get**](CertificatesApi.md#v1_trust_store_certificates_get) | **GET** /v1/trust-store/certificates/fingerprints | Get a list of fingerprints retrieved from the certificates in the VxRail Manager trust store used by the HTTP client.
[**v1_trust_store_certificates_post**](CertificatesApi.md#v1_trust_store_certificates_post) | **POST** /v1/trust-store/certificates | Import certificates into the VxRail Manager trust store.
[**v2_certificates_import_vxm_post**](CertificatesApi.md#v2_certificates_import_vxm_post) | **POST** /v2/certificates/import-vxm | Update the VxRail Manager certificate(Version 2)
[**v3_certificates_import_vxm_post**](CertificatesApi.md#v3_certificates_import_vxm_post) | **POST** /v3/certificates/import-vxm | Update the VxRail Manager certificate(Version 3)

# **v1_certificates_csr_post**
> VxMCsrResponse v1_certificates_csr_post(body)

Generate a Certificate Signing Request.

Generate a CSR with the given parameters. 

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
body = swagger_client.VxMCsrSpec() # VxMCsrSpec | The VxRail Manager parameters to generate a CSR.

try:
    # Generate a Certificate Signing Request.
    api_response = api_instance.v1_certificates_csr_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_certificates_csr_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VxMCsrSpec**](VxMCsrSpec.md)| The VxRail Manager parameters to generate a CSR. | 

### Return type

[**VxMCsrResponse**](VxMCsrResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_certificates_import_vxm_post**
> VxMCertificateResponse v1_certificates_import_vxm_post(body)

Update the VxRail Manager certificate(Version 1)

Update the VxRail Manager certificate.

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
body = swagger_client.VxMCertificateSpec() # VxMCertificateSpec | Parameters of the VxRail Manager certificate to update

try:
    # Update the VxRail Manager certificate(Version 1)
    api_response = api_instance.v1_certificates_import_vxm_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_certificates_import_vxm_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VxMCertificateSpec**](VxMCertificateSpec.md)| Parameters of the VxRail Manager certificate to update | 

### Return type

[**VxMCertificateResponse**](VxMCertificateResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_certificates_scep_config_get**
> ScepConfigResponse v1_certificates_scep_config_get()

Get automated renewal configurations of the certificate

Automated renewal configurations of the VxRail Manager TLS certificate

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))

try:
    # Get automated renewal configurations of the certificate
    api_response = api_instance.v1_certificates_scep_config_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_certificates_scep_config_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ScepConfigResponse**](ScepConfigResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_certificates_scep_config_post**
> ScepConfigResponse v1_certificates_scep_config_post(body)

Update automated renewal configurations of certificate through SCEP

Udpate automated renewal configurations of the VxRail Manager TLS certificate through SCEP

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
body = swagger_client.ScepConfigPostSpec() # ScepConfigPostSpec | Automated renewal configurations of the VxRail Manager TLS certificate

try:
    # Update automated renewal configurations of certificate through SCEP
    api_response = api_instance.v1_certificates_scep_config_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_certificates_scep_config_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ScepConfigPostSpec**](ScepConfigPostSpec.md)| Automated renewal configurations of the VxRail Manager TLS certificate | 

### Return type

[**ScepConfigResponse**](ScepConfigResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_certificates_scep_status_get**
> ScepStatusGetResponse v1_certificates_scep_status_get()

Get automated renewal status of the certificate

Automated renewal status of the VxRail Manager TLS certificate

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))

try:
    # Get automated renewal status of the certificate
    api_response = api_instance.v1_certificates_scep_status_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_certificates_scep_status_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ScepStatusGetResponse**](ScepStatusGetResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_certificates_validate_post**
> v1_certificates_validate_post(body)

Verify the certificate

Verify the VxRail Manager certificate.

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
body = swagger_client.VxMCertificateValidateSpec() # VxMCertificateValidateSpec | Certificate to be validated.

try:
    # Verify the certificate
    api_instance.v1_certificates_validate_post(body)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_certificates_validate_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VxMCertificateValidateSpec**](VxMCertificateValidateSpec.md)| Certificate to be validated. | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_trust_store_certificates_fingerprint_delete**
> v1_trust_store_certificates_fingerprint_delete(fingerprint)

Delete the certificate file from the VxRail Manager trust store according to the fingerprint.

API to delete certificate file from the VxRail Manager trust store according to fingerprint.

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
fingerprint = 'fingerprint_example' # str | The fingerprint certificate to delete.

try:
    # Delete the certificate file from the VxRail Manager trust store according to the fingerprint.
    api_instance.v1_trust_store_certificates_fingerprint_delete(fingerprint)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_trust_store_certificates_fingerprint_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fingerprint** | **str**| The fingerprint certificate to delete. | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_trust_store_certificates_fingerprint_get**
> CertificateContentInfo v1_trust_store_certificates_fingerprint_get(fingerprint)

Search the VxRail Manager trust store and get the certificate content information (PEM form) according to fingerprint parameter.

API to search and get the certificate content from the VxRail Manager trust store according to the fingerprint parameter.

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
fingerprint = 'fingerprint_example' # str | The fingerprint certificate you want to query.

try:
    # Search the VxRail Manager trust store and get the certificate content information (PEM form) according to fingerprint parameter.
    api_response = api_instance.v1_trust_store_certificates_fingerprint_get(fingerprint)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_trust_store_certificates_fingerprint_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fingerprint** | **str**| The fingerprint certificate you want to query. | 

### Return type

[**CertificateContentInfo**](CertificateContentInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_trust_store_certificates_get**
> TrustStoreFingerprintsInfo v1_trust_store_certificates_get()

Get a list of fingerprints retrieved from the certificates in the VxRail Manager trust store used by the HTTP client.

API to retrieve a fingerprint list (using the open SSL command to get the certificate fingerprints in VxRail Manager trust store).

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))

try:
    # Get a list of fingerprints retrieved from the certificates in the VxRail Manager trust store used by the HTTP client.
    api_response = api_instance.v1_trust_store_certificates_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_trust_store_certificates_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**TrustStoreFingerprintsInfo**](TrustStoreFingerprintsInfo.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_trust_store_certificates_post**
> v1_trust_store_certificates_post(body)

Import certificates into the VxRail Manager trust store.

API to import certificates into the VxRail Manager trust store according to the certificates content list.

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
body = swagger_client.CertificateContentSpec() # CertificateContentSpec | Provide the content of the certificate to be imported (PEM form).

try:
    # Import certificates into the VxRail Manager trust store.
    api_instance.v1_trust_store_certificates_post(body)
except ApiException as e:
    print("Exception when calling CertificatesApi->v1_trust_store_certificates_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CertificateContentSpec**](CertificateContentSpec.md)| Provide the content of the certificate to be imported (PEM form). | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v2_certificates_import_vxm_post**
> VxMCertificateV2Info v2_certificates_import_vxm_post(body)

Update the VxRail Manager certificate(Version 2)

Async api to update the VxRail Manager certificate.

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
body = swagger_client.VxMCertificateSpec() # VxMCertificateSpec | Parameters of the VxRail Manager certificate to update

try:
    # Update the VxRail Manager certificate(Version 2)
    api_response = api_instance.v2_certificates_import_vxm_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v2_certificates_import_vxm_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VxMCertificateSpec**](VxMCertificateSpec.md)| Parameters of the VxRail Manager certificate to update | 

### Return type

[**VxMCertificateV2Info**](VxMCertificateV2Info.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v3_certificates_import_vxm_post**
> VxMCertificateV2Info v3_certificates_import_vxm_post(body)

Update the VxRail Manager certificate(Version 3)

Asynchronous API to update the VxRail Manager certificate.

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
api_instance = swagger_client.CertificatesApi(swagger_client.ApiClient(configuration))
body = swagger_client.VxMCertificateV3Spec() # VxMCertificateV3Spec | The VxRail Manager certificate parameters for update.

try:
    # Update the VxRail Manager certificate(Version 3)
    api_response = api_instance.v3_certificates_import_vxm_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CertificatesApi->v3_certificates_import_vxm_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VxMCertificateV3Spec**](VxMCertificateV3Spec.md)| The VxRail Manager certificate parameters for update. | 

### Return type

[**VxMCertificateV2Info**](VxMCertificateV2Info.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

