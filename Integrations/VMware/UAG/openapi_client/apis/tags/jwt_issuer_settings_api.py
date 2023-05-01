# coding: utf-8

"""
    Unified Access Gateway REST API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.2
    Generated by: https://openapi-generator.tech
"""

from openapi_client.paths.v1_config_jwt_issuer.post import CreateJwtIssuerSettings
from openapi_client.paths.v1_config_jwt_issuer_name.delete import DeleteJwtIssuerSettings
from openapi_client.paths.v1_config_jwt_issuer.get import GetAllJwtIssuerSettings
from openapi_client.paths.v1_config_jwt_issuer_name.get import GetJwtIssuerSettings
from openapi_client.paths.v1_config_jwt_issuer.put import UpdateJwtIssuerSettings


class JWTIssuerSettingsApi(
    CreateJwtIssuerSettings,
    DeleteJwtIssuerSettings,
    GetAllJwtIssuerSettings,
    GetJwtIssuerSettings,
    UpdateJwtIssuerSettings,
):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """
    pass