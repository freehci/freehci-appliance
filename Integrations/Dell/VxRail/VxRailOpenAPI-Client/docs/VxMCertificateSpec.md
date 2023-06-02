# VxMCertificateSpec

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cert** | **str** | The content of the new certificate in PEM format. | 
**primary_key** | **str** | The contents of the private key in PEM format. Only an RSA private key is allowed. | 
**root_cert_chain** | **str** | Contents of the certificate chain in PEM format. The root CA certificate comes first, followed by the intermediate CA certificates (if any). | 
**password** | **str** | The password for the new .pfx file. It is deprecated from 7.0.380 release. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

