# coding: utf-8

"""
    Unified Access Gateway REST API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.2
    Generated by: https://openapi-generator.tech
"""

from datetime import date, datetime  # noqa: F401
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401

import frozendict  # noqa: F401

from openapi_client import schemas  # noqa: F401


class WS1IntelligenceData(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        class properties:
        
            @staticmethod
            def oauth_client() -> typing.Type['WS1IntelligenceOAuthClient']:
                return WS1IntelligenceOAuthClient
            events_base_url = schemas.StrSchema
            token_endpoint = schemas.StrSchema
            api_base_url = schemas.StrSchema
            __annotations__ = {
                "oauth_client": oauth_client,
                "events_base_url": events_base_url,
                "token_endpoint": token_endpoint,
                "api_base_url": api_base_url,
            }
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["oauth_client"]) -> 'WS1IntelligenceOAuthClient': ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["events_base_url"]) -> MetaOapg.properties.events_base_url: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["token_endpoint"]) -> MetaOapg.properties.token_endpoint: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["api_base_url"]) -> MetaOapg.properties.api_base_url: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["oauth_client", "events_base_url", "token_endpoint", "api_base_url", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["oauth_client"]) -> typing.Union['WS1IntelligenceOAuthClient', schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["events_base_url"]) -> typing.Union[MetaOapg.properties.events_base_url, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["token_endpoint"]) -> typing.Union[MetaOapg.properties.token_endpoint, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["api_base_url"]) -> typing.Union[MetaOapg.properties.api_base_url, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["oauth_client", "events_base_url", "token_endpoint", "api_base_url", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        oauth_client: typing.Union['WS1IntelligenceOAuthClient', schemas.Unset] = schemas.unset,
        events_base_url: typing.Union[MetaOapg.properties.events_base_url, str, schemas.Unset] = schemas.unset,
        token_endpoint: typing.Union[MetaOapg.properties.token_endpoint, str, schemas.Unset] = schemas.unset,
        api_base_url: typing.Union[MetaOapg.properties.api_base_url, str, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'WS1IntelligenceData':
        return super().__new__(
            cls,
            *_args,
            oauth_client=oauth_client,
            events_base_url=events_base_url,
            token_endpoint=token_endpoint,
            api_base_url=api_base_url,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.ws1_intelligence_o_auth_client import WS1IntelligenceOAuthClient
