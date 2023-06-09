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


class KerberosKeyTabSettings(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        required = {
            "keyTab",
        }
        
        class properties:
            keyTab = schemas.StrSchema
            principalName = schemas.StrSchema
            keyTabFilePath = schemas.StrSchema
            realm = schemas.StrSchema
            __annotations__ = {
                "keyTab": keyTab,
                "principalName": principalName,
                "keyTabFilePath": keyTabFilePath,
                "realm": realm,
            }
    
    keyTab: MetaOapg.properties.keyTab
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["keyTab"]) -> MetaOapg.properties.keyTab: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["principalName"]) -> MetaOapg.properties.principalName: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["keyTabFilePath"]) -> MetaOapg.properties.keyTabFilePath: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["realm"]) -> MetaOapg.properties.realm: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["keyTab", "principalName", "keyTabFilePath", "realm", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["keyTab"]) -> MetaOapg.properties.keyTab: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["principalName"]) -> typing.Union[MetaOapg.properties.principalName, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["keyTabFilePath"]) -> typing.Union[MetaOapg.properties.keyTabFilePath, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["realm"]) -> typing.Union[MetaOapg.properties.realm, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["keyTab", "principalName", "keyTabFilePath", "realm", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        keyTab: typing.Union[MetaOapg.properties.keyTab, str, ],
        principalName: typing.Union[MetaOapg.properties.principalName, str, schemas.Unset] = schemas.unset,
        keyTabFilePath: typing.Union[MetaOapg.properties.keyTabFilePath, str, schemas.Unset] = schemas.unset,
        realm: typing.Union[MetaOapg.properties.realm, str, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'KerberosKeyTabSettings':
        return super().__new__(
            cls,
            *_args,
            keyTab=keyTab,
            principalName=principalName,
            keyTabFilePath=keyTabFilePath,
            realm=realm,
            _configuration=_configuration,
            **kwargs,
        )
