# coding: utf-8

"""
    Unified Access Gateway REST API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.2
    Generated by: https://openapi-generator.tech
"""

from openapi_client.paths.v1_config_idp_ext_metadata_entity_id__.get import GetIdpMetadata
from openapi_client.paths.v1_config_idp_ext_metadata.get import GetIdpMetadata1
from openapi_client.paths.v1_config_idp_ext_metadata.put import PutIdpMetadata


class IdentityProviderExternalMetadataApi(
    GetIdpMetadata,
    GetIdpMetadata1,
    PutIdpMetadata,
):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """
    pass
