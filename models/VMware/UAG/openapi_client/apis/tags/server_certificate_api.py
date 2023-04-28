# coding: utf-8

"""
    Unified Access Gateway REST API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.2
    Generated by: https://openapi-generator.tech
"""

from openapi_client.paths.v1_config_certs_ssl.get import GetSslCertificate
from openapi_client.paths.v1_config_certs_ssl_entity.get import GetSslCertificate1
from openapi_client.paths.v1_config_certs_ssl_entity.put import UpdateSslCertificate
from openapi_client.paths.v1_config_certs_ssl.put import UpdateSslCertificate1
from openapi_client.paths.v1_config_certs_ssl_pfx_entity.put import UpdateSslCertificateWithPfx
from openapi_client.paths.v1_config_certs_ssl_pfx.put import UpdateSslCertificateWithPfx1


class ServerCertificateApi(
    GetSslCertificate,
    GetSslCertificate1,
    UpdateSslCertificate,
    UpdateSslCertificate1,
    UpdateSslCertificateWithPfx,
    UpdateSslCertificateWithPfx1,
):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """
    pass
