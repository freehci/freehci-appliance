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


class CoreDumpSettings(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        class properties:
            
            
            class maxSizeMb(
                schemas.Int32Schema
            ):
                pass
            
            
            class maxTimeSeconds(
                schemas.Int32Schema
            ):
                pass
            __annotations__ = {
                "maxSizeMb": maxSizeMb,
                "maxTimeSeconds": maxTimeSeconds,
            }
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["maxSizeMb"]) -> MetaOapg.properties.maxSizeMb: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["maxTimeSeconds"]) -> MetaOapg.properties.maxTimeSeconds: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["maxSizeMb", "maxTimeSeconds", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["maxSizeMb"]) -> typing.Union[MetaOapg.properties.maxSizeMb, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["maxTimeSeconds"]) -> typing.Union[MetaOapg.properties.maxTimeSeconds, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["maxSizeMb", "maxTimeSeconds", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        maxSizeMb: typing.Union[MetaOapg.properties.maxSizeMb, decimal.Decimal, int, schemas.Unset] = schemas.unset,
        maxTimeSeconds: typing.Union[MetaOapg.properties.maxTimeSeconds, decimal.Decimal, int, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'CoreDumpSettings':
        return super().__new__(
            cls,
            *_args,
            maxSizeMb=maxSizeMb,
            maxTimeSeconds=maxTimeSeconds,
            _configuration=_configuration,
            **kwargs,
        )
