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


class NicSettingsList(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        required = {
            "nicSettingsList",
        }
        
        class properties:
            
            
            class nicSettingsList(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    
                    @staticmethod
                    def items() -> typing.Type['NicSettings']:
                        return NicSettings
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple['NicSettings'], typing.List['NicSettings']],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'nicSettingsList':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> 'NicSettings':
                    return super().__getitem__(i)
            __annotations__ = {
                "nicSettingsList": nicSettingsList,
            }
    
    nicSettingsList: MetaOapg.properties.nicSettingsList
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["nicSettingsList"]) -> MetaOapg.properties.nicSettingsList: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["nicSettingsList", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["nicSettingsList"]) -> MetaOapg.properties.nicSettingsList: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["nicSettingsList", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        nicSettingsList: typing.Union[MetaOapg.properties.nicSettingsList, list, tuple, ],
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'NicSettingsList':
        return super().__new__(
            cls,
            *_args,
            nicSettingsList=nicSettingsList,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.nic_settings import NicSettings